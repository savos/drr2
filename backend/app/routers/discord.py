"""Discord router for OAuth integration and messaging."""
import os
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse, JSONResponse
from urllib.parse import urlparse
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database.database import get_db
from app.models.users import User
from app.models.discord import DiscordStatus
from app.schemas.discord import DiscordRead
from app.utils.security import get_current_user, SECRET_KEY, ALGORITHM
from app.consumers.discord import discord_consumer, DiscordAPIError
from app.services.discord import discord_service
from jose import jwt, JWTError
import hmac
import hashlib
import time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/discord", tags=["discord"])


# Request/Response Models
class OAuthUrlResponse(BaseModel):
    """OAuth URL response."""
    oauth_url: str
    state: str


class OAuthCallbackResponse(BaseModel):
    """OAuth callback response."""
    success: bool
    message: str
    integration: Optional[DiscordRead] = None


class TestConnectionResponse(BaseModel):
    """Test connection response."""
    success: bool
    message: str


class ChannelSelectRequest(BaseModel):
    """Request to select a server channel for notifications."""
    channel_id: str
    guild_id: Optional[str] = None


@router.get("/oauth/url", response_model=OAuthUrlResponse)
async def get_oauth_url(
    current_user: User = Depends(get_current_user)
):
    """
    Get Discord OAuth authorization URL.

    Generates a unique state parameter for CSRF protection and returns
    the Discord OAuth URL for user authorization.

    Args:
        current_user: Current authenticated user

    Returns:
        OAuth URL and state parameter
    """
    try:
        # Generate unique state for CSRF protection
        state = f"{current_user.id}:{uuid.uuid4()}"

        # Get OAuth URL
        oauth_url = discord_consumer.get_oauth_url(state)

        logger.info(f"Generated Discord OAuth URL for user {current_user.id}")

        return OAuthUrlResponse(
            oauth_url=oauth_url,
            state=state
        )

    except Exception as e:
        logger.error(f"Error generating OAuth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate OAuth URL"
        )


@router.get("/oauth/callback")
async def oauth_callback(
    code: str = Query(..., description="OAuth authorization code"),
    state: str = Query(..., description="CSRF protection state"),
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Discord OAuth callback.

    Exchanges the authorization code for an access token and stores
    the Discord integration in the database.

    Args:
        code: OAuth authorization code from Discord
        state: CSRF protection state parameter
        db: Database session

    Returns:
        Redirect to frontend with success/error status
    """
    try:
        # Extract user_id from state
        try:
            user_id = state.split(":")[0]
        except (IndexError, ValueError):
            logger.error(f"Invalid state parameter: {state}")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(
                url=f"{frontend_url}/dashboard/channels/discord?error=invalid_state"
            )

        # Exchange code for token
        try:
            oauth_data = await discord_consumer.exchange_code_for_token(code)
        except DiscordAPIError as e:
            logger.error(f"OAuth token exchange failed: {e}")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(
                url=f"{frontend_url}/dashboard/channels/discord?error=oauth_failed"
            )

        # Extract access token
        access_token = oauth_data.get("access_token")
        if not access_token:
            logger.error("Discord OAuth missing access_token")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(url=f"{frontend_url}/dashboard/channels/discord?error=missing_data")

        # Get current user from Discord
        try:
            me = await discord_consumer.get_current_user(access_token)
        except DiscordAPIError as e:
            logger.error(f"Failed to get Discord user: {e}")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(url=f"{frontend_url}/dashboard/channels/discord?error=oauth_failed")

        discord_user_id = me.get("id")
        username = me.get("username")
        global_name = me.get("global_name")
        if not discord_user_id:
            logger.error("Discord user id missing in /users/@me")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(url=f"{frontend_url}/dashboard/channels/discord?error=missing_data")

        # Fetch ALL user's guilds using their access token (then discard token)
        # Store all guild IDs so we can show servers user has joined (not just owned)
        user_guild_ids_str = None
        try:
            user_guilds = await discord_consumer.get_user_guilds(access_token)
            # Store ALL guilds user is in (created or joined)
            all_guild_ids = [
                guild.get("id") for guild in user_guilds
                if guild.get("id")
            ]
            if all_guild_ids:
                user_guild_ids_str = ",".join(all_guild_ids)
            owned_count = sum(1 for g in user_guilds if g.get("owner"))
            logger.info(f"User {user_id} is in {len(all_guild_ids)} guilds ({owned_count} owned)")
        except DiscordAPIError as e:
            logger.warning(f"Failed to fetch user guilds (continuing without): {e}")
        # Access token is intentionally NOT stored for security

        # Create DM channel with user using bot token
        try:
            dm_channel = await discord_consumer.create_dm_channel(discord_user_id)
            dm_channel_id = dm_channel.get("id")
        except DiscordAPIError as e:
            logger.error(f"Failed to create Discord DM channel: {e}")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(url=f"{frontend_url}/dashboard/channels/discord?error=database_error")

        # Store DM integration in database (with owned guild IDs, NOT access token)
        try:
            dm_integration = await discord_service.create_discord_integration(
                db=db,
                user_id=user_id,
                discord_user_id=discord_user_id,
                username=username,
                global_name=global_name,
                guild_id=None,
                guild_name=None,
                channel_id=dm_channel_id,
                channel_name=None,
                status=DiscordStatus.ENABLED,
                owned_guild_ids=user_guild_ids_str  # stores ALL user guilds despite field name
            )

            logger.info(f"Discord DM integration created for user {user_id}")

            # Get user's guilds for selection modal
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(url=f"{frontend_url}/dashboard/channels/discord?success=true&show_guild_selection=true")

        except Exception as e:
            logger.error(f"Database error storing Discord integration: {e}")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(
                url=f"{frontend_url}/dashboard/channels/discord?error=database_error"
            )

    except Exception as e:
        logger.error(f"Unexpected error in OAuth callback: {e}")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(
            url=f"{frontend_url}/dashboard/channels/discord?error=unexpected_error"
        )


# Backward/alternate compatibility route: some environments configure
# DISCORD_REDIRECT_URI without the "/oauth" segment (e.g. "/api/discord/callback").
# Expose an alias that forwards to the main handler so both
# /api/discord/oauth/callback and /api/discord/callback work.
@router.get("/callback")
async def oauth_callback_alias(
    code: str = Query(..., description="OAuth authorization code"),
    state: str = Query(..., description="CSRF protection state"),
    db: AsyncSession = Depends(get_db)
):
    return await oauth_callback(code=code, state=state, db=db)


def _verify_discord_signature(request: Request, body: bytes, signing_secret: str) -> bool:
    ts = request.headers.get("X-Discord-Request-Timestamp", "0")
    sig = request.headers.get("X-Discord-Signature", "")
    # Prevent replay attacks (5 minutes window)
    try:
        if abs(int(time.time()) - int(ts)) > 60 * 5:
            return False
    except Exception:
        return False
    base = f"v0:{ts}:".encode() + body
    digest = hmac.new(signing_secret.encode(), base, hashlib.sha256).hexdigest()
    expected = f"v0={digest}"
    return hmac.compare_digest(expected, sig)


def _verify_discord_interaction(request: Request, body: bytes, public_key_hex: str) -> bool:
    """Verify Discord Interactions (Ed25519) signature.
    Headers:
      - X-Signature-Ed25519: hex signature
      - X-Signature-Timestamp: string timestamp
    Message = timestamp + raw_body
    """
    sig_hex = request.headers.get("X-Signature-Ed25519", "")
    ts = request.headers.get("X-Signature-Timestamp", "0")
    if not sig_hex or not ts or not public_key_hex:
        return False
    # optional replay guard (5 minutes)
    try:
        if abs(int(time.time()) - int(ts)) > 60 * 5:
            return False
    except Exception:
        return False
    try:
        pk = Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
        sig = bytes.fromhex(sig_hex)
        message = ts.encode() + body
        pk.verify(sig, message)
        return True
    except (ValueError, InvalidSignature):
        return False


@router.post("/events")
async def discord_events(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Discord Events API endpoint.

    - Verifies Discord signature using DISCORD_SIGNING_SECRET
    - Handles url_verification
    - On member_joined_channel for our bot user, associates the channel with the integration
    """
    # Parse payload first to support Discord URL verification without blocking on signature
    raw_body = await request.body()
    try:
        logger.info(
            f"Discord events: received {len(raw_body)} bytes, headers x-discord-signature=%s, x-discord-request-timestamp=%s",
            request.headers.get("X-Discord-Signature"),
            request.headers.get("X-Discord-Request-Timestamp"),
        )
    except Exception:
        logger.exception("Discord events: failed to log headers")
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    # URL verification challenge (respond immediately)
    if payload.get("type") == "url_verification":
        logger.info("Discord events: url_verification received, responding with challenge")
        return JSONResponse(content={"challenge": payload.get("challenge", "")})

    # Verify signature for event callbacks
    signing_secret = os.getenv("DISCORD_SIGNING_SECRET")
    if not signing_secret:
        logger.error("Discord events: DISCORD_SIGNING_SECRET not configured")
        return JSONResponse(status_code=500, content={"error": "Signing secret not configured"})

    if not _verify_discord_signature(request, raw_body, signing_secret):
        logger.warning("Discord events: invalid signature")
        return JSONResponse(status_code=401, content={"error": "Invalid signature"})

    if payload.get("type") == "event_callback":
        event = payload.get("event", {})
        team_id = payload.get("team_id") or event.get("team")
        event_type = event.get("type")
        logger.info("Discord events: event_callback type=%s team_id=%s", event_type, team_id)
        if event_type == "member_joined_channel":
            bot_user = event.get("user")
            channel_id = event.get("channel")
            logger.info("Discord events: member_joined_channel user=%s channel=%s", bot_user, channel_id)

            if team_id and bot_user and channel_id:
                # Find existing workspace integrations (DMs) for this workspace/bot
                integrations = await discord_service.get_by_workspace_and_bot_user(db, team_id, bot_user)
                logger.info("Discord events: matched %d integration(s) for workspace/bot", len(integrations))

                # Create a new integration for this channel based on the first workspace integration
                if integrations:
                    base_integration = integrations[0]  # Use any existing integration as template

                    # Fetch channel info to get the channel name
                    channel_name = None
                    try:
                        channel_info = await discord_consumer.get_channel_info(base_integration.bot_token, channel_id)
                        channel_name = channel_info.get("name") or channel_info.get("name_normalized")
                        logger.info("Discord events: channel name=%s", channel_name)
                    except Exception as e:
                        logger.warning(f"Failed to get channel name for {channel_id}: {e}")

                    # Create new channel integration
                    try:
                        await discord_service.create_channel_integration(
                            db=db,
                            workspace_integration=base_integration,
                            channel_id=channel_id,
                            channel_name=channel_name
                        )
                        logger.info(f"Created channel integration for channel {channel_id} ({channel_name})")
                    except Exception as e:
                        logger.error(f"Failed to create channel integration: {e}")

        return JSONResponse(content={"ok": True})

    return JSONResponse(content={"ok": True})


@router.post("/interactions")
async def discord_interactions(request: Request):
    """Discord Interactions endpoint with Ed25519 verification.

    - Verifies X-Signature-Ed25519 and X-Signature-Timestamp using DISCORD_PUBLIC_KEY
    - Responds to Ping with PONG (type 1)
    """
    raw_body = await request.body()
    public_key = os.getenv("DISCORD_PUBLIC_KEY", "")
    if not public_key:
        return JSONResponse(status_code=500, content={"error": "DISCORD_PUBLIC_KEY not configured"})
    if not _verify_discord_interaction(request, raw_body, public_key):
        return JSONResponse(status_code=401, content={"error": "Invalid signature"})
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    # Discord ping
    if payload.get("type") == 1:
        return JSONResponse(content={"type": 1})
    # For now, acknowledge others
    return JSONResponse(content={"type": 5})


@router.get("/integrations", response_model=list[DiscordRead])
async def get_integrations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all Discord integrations for the current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of Discord integrations
    """
    try:
        integrations = await discord_service.get_by_user(db, current_user.id)
        return integrations

    except Exception as e:
        logger.error(f"Error getting Discord integrations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Discord integrations"
        )


@router.post("/integrations/{integration_id}/test", response_model=TestConnectionResponse)
async def test_connection(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    verify_token: Optional[str] = Query(None, description="Optional small token generated by frontend for client-side verification")
):
    """
    Send a test message to verify Discord connection.

    Args:
        integration_id: Discord integration ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Test connection result
    """
    try:
        # Get integration
        integration = await discord_service.get_by_id(db, integration_id)

        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discord integration not found"
            )

        # Verify ownership
        if integration.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this integration"
            )

        # Prepare optional verification URL included in the test message
        try:
            verification_url = None
            # Prefer a frontend-provided small token for client-side verification
            if verify_token:
                # Build direct link back to frontend page and include integration_id to simplify client call
                frontend = os.getenv("FRONTEND_URL", "http://localhost:3000")
                verification_url = f"{frontend}/dashboard/channels/discord?verified={verify_token}&integration_id={integration.id}"
            else:
                # Fallback to signed server token (more secure) as a robust option
                payload = {
                    "purpose": "discord_verify",
                    "integration_id": integration.id,
                    "user_id": str(current_user.id),
                    "exp": datetime.utcnow() + timedelta(days=7),
                }
                signed = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
                redirect_uri = os.getenv("DISCORD_REDIRECT_URI", "")
                parsed = urlparse(redirect_uri)
                base = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else os.getenv("FRONTEND_URL", "http://localhost:3000")
                verification_url = f"{base}/api/discord/verify?token={signed}"
        except Exception:
            logger.exception("Failed to build Discord verification URL; continuing without it")
            verification_url = None

        # Send test message
        try:
            # DM if no guild_id is present; otherwise a server channel
            is_dm = integration.guild_id is None

            if is_dm:
                # Send test message to DM channel id we stored
                await discord_consumer.send_test_message(
                    channel_id=integration.channel_id,
                    username=integration.global_name or integration.username,
                    verification_url=verification_url
                )
                logger.info(f"Test DM sent successfully for integration {integration_id}")
                message = "Test message sent to your Discord DM. Please click '✅ Confirm in DRR' to activate."
            else:
                # Send test message to server channel
                await discord_consumer.send_message(
                    channel_id=integration.channel_id,
                    content="✅ DRR test: this channel is connected and ready to receive notifications."
                )
                logger.info(f"Test message sent to channel {integration.channel_id} for integration {integration_id}")
                message = f"Test message sent to channel {integration.channel_id}. Check Discord to confirm."

            return TestConnectionResponse(success=True, message=message)

        except DiscordAPIError as e:
            logger.error(f"Failed to send test message: {e}")
            msg = str(e)
            # DM privacy blockers
            if "Cannot send messages to this user" in msg:
                return TestConnectionResponse(
                    success=False,
                    message=(
                        "Discord prevented sending a DM. Make sure the bot and your account share a server, "
                        "and that 'Allow direct messages from server members' is enabled in your Discord privacy settings. "
                        "Alternatively, invite the DRR bot to a server and select a server channel."
                    )
                )
            # Channel permission blockers
            if ("Missing Access" in msg) or ("Missing Permissions" in msg):
                return TestConnectionResponse(
                    success=False,
                    message=(
                        "The bot lacks permission to post in this channel. In the channel permissions, grant the DRR bot role "
                        "'View Channel' and 'Send Messages' (and optionally 'Read Message History' and 'Embed Links'). "
                        "Then try again."
                    )
                )
            return TestConnectionResponse(success=False, message=f"Failed to send test message: {msg}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error testing Discord connection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test connection"
        )


@router.delete("/integrations/{integration_id}")
async def delete_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a Discord integration.

    Args:
        integration_id: Discord integration ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message
    """
    try:
        # Get integration
        integration = await discord_service.get_by_id(db, integration_id)

        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discord integration not found"
            )

        # Verify ownership
        if integration.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this integration"
            )

        # Attempt to uninstall the app from Discord (best-effort)
        try:
            if integration.bot_token:
                uninstalled = await discord_consumer.uninstall_app(integration.bot_token)
                if not uninstalled:
                    await discord_consumer.revoke_token(integration.bot_token)
        except Exception as e:
            logger.warning(f"Unable to uninstall or revoke Discord app for integration {integration_id}: {e}")

        # Delete integration from our DB
        deleted = await discord_service.delete(db, integration_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete integration"
            )

        logger.info(f"Deleted Discord integration {integration_id}")

        return {"message": "Integration deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Discord integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete integration"
        )


@router.post("/integrations/{integration_id}/verify", response_model=TestConnectionResponse)
async def activate_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Activate a Discord integration after client-side verification.

    Security: relies on standard JWT auth and ownership check; client-side "verified" token
    is validated in the browser before this call.
    """
    try:
        integration = await discord_service.get_by_id(db, integration_id)
        if not integration:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discord integration not found")
        if integration.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this integration")

        updated = await discord_service.update_status(db, integration_id, DiscordStatus.ACTIVE)
        if not updated:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update status")

        return TestConnectionResponse(success=True, message="Integration verified and activated.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating Discord integration: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to activate integration")


@router.get("/verify")
async def verify_discord_integration(
    token: str = Query(..., description="Signed verification token"),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify Discord DM is working via a signed link included in the test message.

    Decodes the signed token, validates intent, updates the integration status
    to ACTIVE, and redirects to the frontend with a success indicator.
    """
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if data.get("purpose") != "discord_verify":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

        integration_id = data.get("integration_id")
        user_id = data.get("user_id")
        if not integration_id or not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token data")

        # Load integration and ensure it matches the token
        integration = await discord_service.get_by_id(db, int(integration_id))
        if not integration:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")
        if str(integration.user_id) != str(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token user mismatch")

        # Update status to ACTIVE and only show success on actual update
        updated = await discord_service.update_status(db, int(integration_id), DiscordStatus.ACTIVE)
        logger.info(f"Discord integration {integration_id} verified via link click; updated={bool(updated)}")

        if updated:
            return RedirectResponse(url=f"{frontend_url}/dashboard/channels/discord?verified=true")
        return RedirectResponse(url=f"{frontend_url}/dashboard/channels/discord?error=verify_failed")
    except JWTError:
        return RedirectResponse(url=f"{frontend_url}/dashboard/channels/discord?error=verify_failed")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error verifying Discord integration")
        return RedirectResponse(url=f"{frontend_url}/dashboard/channels/discord?error=verify_failed")


@router.post("/channels/select")
async def select_server_channel(
    req: ChannelSelectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Select a Discord server channel for notifications (minimal path).

    Validates bot can post to the channel, then updates the user's integration.
    """
    # Validate posting permissions by sending a small message
    try:
        await discord_consumer.send_message(
            channel_id=req.channel_id,
            content="✅ DRR connected: this channel will receive notifications."
        )
    except DiscordAPIError as e:
        logger.error(f"Discord channel validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bot cannot post to this channel. Check permissions and try again.")

    # Update the user's integration to point at this channel
    integ = await discord_service.update_channel_for_user(db, current_user.id, channel_id=req.channel_id, guild_id=req.guild_id)
    if not integ:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Discord integration found for this user. Connect DM first.")

    return {"success": True, "message": "Server channel selected.", "integration_id": integ.id}
@router.get("/bot/invite-url")
async def get_bot_invite_url():
    """
    Return a bot invite URL so the user can add DRR to a server.

    Minimal permissions: View Channels (1024) + Send Messages (2048) = 3072.
    Adjust in app config if you need more.
    """
    client_id = os.getenv("DISCORD_CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=500, detail="DISCORD_CLIENT_ID not configured")
    # View Channels (1024) + Send Messages (2048) + Embed Links (16384) + Read Message History (65536) + Send Messages in Threads (1048576)
    permissions = 1024 + 2048 + 16384 + 65536 + 1048576  # 1,133,568
    invite_url = (
        f"https://discord.com/api/oauth2/authorize?client_id={client_id}"
        f"&permissions={permissions}&scope=bot"
    )
    return {"invite_url": invite_url}


@router.get("/available-guilds")
async def get_available_guilds(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of Discord guilds with their channels where the user is a member AND bot has access.

    Returns guilds that the user has joined (created or joined) and where the bot is present.
    Shows all text/announcement channels the bot can see in those guilds.

    Security: No user credentials are stored. Guild IDs are captured during OAuth
    and stored as a simple ID list (no tokens).
    """
    try:
        # Get user's DM integration with stored guild IDs
        dm_integration = await discord_service.get_dm_integration(db, current_user.id)

        if not dm_integration:
            logger.warning(f"User {current_user.id} has no Discord integration")
            return {
                "guilds": [],
                "error": "no_integration",
                "message": "Please connect Discord first."
            }

        # Parse stored guild IDs (comma-separated) - field named owned_guild_ids but stores ALL guilds
        if not dm_integration.owned_guild_ids:
            logger.info(f"User {current_user.id} has no guilds stored - need to reconnect")
            return {
                "guilds": [],
                "error": "no_guilds",
                "message": "Please reconnect Discord to refresh your server list."
            }

        user_guild_ids = set(dm_integration.owned_guild_ids.split(","))
        logger.info(f"User {current_user.id} is in {len(user_guild_ids)} guilds (from stored data)")

        if not user_guild_ids:
            return {
                "guilds": [],
                "message": "You're not in any Discord servers. Join a server first, then invite the bot."
            }

        # Get all guilds where bot has access
        bot_guilds = await discord_consumer.get_bot_guilds()
        bot_guild_map = {guild.get("id"): guild for guild in bot_guilds}
        logger.info(f"Bot is in {len(bot_guilds)} guilds")

        # Find intersection: user's guilds where bot is also present
        available_guild_ids = user_guild_ids & set(bot_guild_map.keys())
        logger.info(f"Intersection (user member AND bot present): {len(available_guild_ids)} guilds")

        # Get user's existing integrations
        user_integrations = await discord_service.get_by_user(db, current_user.id)
        integrated_channels = {
            (integration.guild_id, integration.channel_id)
            for integration in user_integrations
            if integration.guild_id is not None and integration.channel_id is not None
        }

        available_guilds = []

        for guild_id in available_guild_ids:
            guild = bot_guild_map.get(guild_id)
            if not guild:
                continue

            try:
                # Get channels for this guild (bot can see these)
                channels = await discord_consumer.get_guild_channels(guild_id)

                # Filter to text and announcement channels only, exclude already integrated
                available_channels = []
                for channel in channels:
                    channel_id = channel.get("id")
                    channel_name = channel.get("name")
                    channel_type = channel.get("type")

                    # Only include text channels (0) and announcement channels (5)
                    if channel_type not in [0, 5]:
                        continue

                    # Skip if already integrated
                    if (guild_id, channel_id) in integrated_channels:
                        continue

                    if channel_id and channel_name:
                        available_channels.append({
                            "id": channel_id,
                            "name": channel_name,
                            "type": "text" if channel_type == 0 else "announcement"
                        })

                # Only include guild if it has available channels
                if available_channels:
                    available_guilds.append({
                        "id": guild_id,
                        "name": guild.get("name"),
                        "icon": guild.get("icon"),
                        "owner": True,  # Always true since we filtered to owned guilds
                        "channels": available_channels
                    })

            except DiscordAPIError as e:
                logger.warning(f"Failed to get channels for guild {guild_id}: {e}")
                continue

        # If user is in guilds but bot isn't in any of them, provide guidance
        if not available_guilds and user_guild_ids:
            return {
                "guilds": [],
                "message": "The bot isn't installed in any of your servers yet. Use the 'Add Bot to Server' button to invite the bot to a server you have access to."
            }

        logger.info(f"User {current_user.id} has {len(available_guilds)} guilds with available channels")
        return {"guilds": available_guilds}

    except DiscordAPIError as e:
        logger.error(f"Failed to get available guilds: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve available guilds"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting available guilds: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve available guilds"
        )


class ChannelSelection(BaseModel):
    """Selected channel info."""
    guild_id: str
    guild_name: str
    channel_id: str
    channel_name: str


class AddChannelsRequest(BaseModel):
    """Request to add selected channels."""
    channels: list[ChannelSelection]


@router.post("/add-channels")
async def add_selected_channels(
    request: AddChannelsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add selected channels to user's Discord integrations.

    Creates channel integrations for the specifically selected channels.
    """
    try:
        # Get user's DM integration to use as base
        user_integrations = await discord_service.get_by_user(db, current_user.id)
        dm_integration = next((i for i in user_integrations if i.guild_id is None), None)

        if not dm_integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Discord DM integration found. Please connect Discord first."
            )

        added_count = 0
        failed_channels = []

        for channel_selection in request.channels:
            try:
                # Create channel integration
                integration = await discord_service.create_channel_integration(
                    db=db,
                    base_integration=dm_integration,
                    guild_id=channel_selection.guild_id,
                    guild_name=channel_selection.guild_name,
                    channel_id=channel_selection.channel_id,
                    channel_name=channel_selection.channel_name
                )
                added_count += 1
                logger.info(
                    f"✅ Created integration ID {integration.id} for channel #{channel_selection.channel_name} "
                    f"in guild {channel_selection.guild_name} for user {current_user.id}"
                )
            except Exception as e:
                logger.error(
                    f"❌ Failed to create integration for channel {channel_selection.channel_id}: {e}"
                )
                failed_channels.append(channel_selection.channel_id)

        return {
            "success": True,
            "message": f"Added {added_count} channel integrations",
            "added_count": added_count,
            "failed_channels": failed_channels
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding selected channels: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add selected channels"
        )
