"""Slack router for OAuth integration and messaging."""
import os
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse, JSONResponse
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database.database import get_db
from app.models.users import User
from app.models.slack import SlackStatus
from app.schemas.slack import SlackRead
from app.utils.security import get_current_user, SECRET_KEY, ALGORITHM
from app.consumers.slack import slack_consumer, SlackAPIError
from app.services.slack import slack_service
from jose import jwt, JWTError
import hmac
import hashlib
import time

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/slack", tags=["slack"])


# Request/Response Models
class OAuthUrlResponse(BaseModel):
    """OAuth URL response."""
    oauth_url: str
    state: str


class OAuthCallbackResponse(BaseModel):
    """OAuth callback response."""
    success: bool
    message: str
    integration: Optional[SlackRead] = None


class TestConnectionResponse(BaseModel):
    """Test connection response."""
    success: bool
    message: str


@router.get("/oauth/url", response_model=OAuthUrlResponse)
async def get_oauth_url(
    current_user: User = Depends(get_current_user)
):
    """
    Get Slack OAuth authorization URL.

    Generates a unique state parameter for CSRF protection and returns
    the Slack OAuth URL for user authorization.

    Args:
        current_user: Current authenticated user

    Returns:
        OAuth URL and state parameter
    """
    try:
        # Generate unique state for CSRF protection
        state = f"{current_user.id}:{uuid.uuid4()}"

        # Get OAuth URL
        oauth_url = slack_consumer.get_oauth_url(state)

        logger.info(f"Generated Slack OAuth URL for user {current_user.id}")

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
    Handle Slack OAuth callback.

    Exchanges the authorization code for an access token and stores
    the Slack integration in the database.

    Args:
        code: OAuth authorization code from Slack
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
                url=f"{frontend_url}/dashboard/channels/slack?error=invalid_state"
            )

        # Exchange code for token
        try:
            oauth_data = await slack_consumer.exchange_code_for_token(code)
        except SlackAPIError as e:
            logger.error(f"OAuth token exchange failed: {e}")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(
                url=f"{frontend_url}/dashboard/channels/slack?error=oauth_failed"
            )

        # Extract necessary data
        access_token = oauth_data.get("access_token")
        team = oauth_data.get("team", {})
        authed_user = oauth_data.get("authed_user", {})
        bot_user_id = oauth_data.get("bot_user_id")

        workspace_id = team.get("id")
        workspace_name = team.get("name")
        slack_user_id = authed_user.get("id")
        user_token = authed_user.get("access_token")

        if not all([access_token, workspace_id]):
            logger.error("Missing required OAuth data")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(
                url=f"{frontend_url}/dashboard/channels/slack?error=missing_data"
            )

        # Store DM integration in database
        # For OAuth, we create a DM integration with channel_id = slack_user_id
        try:
            dm_integration = await slack_service.create_slack_integration(
                db=db,
                user_id=user_id,
                workspace_id=workspace_id,
                workspace_name=workspace_name,
                access_token=access_token,
                bot_user_id=bot_user_id,
                slack_user_id=slack_user_id,
                user_token=user_token,
                channel_id=slack_user_id,  # DM channel ID is the user's ID
                channel_name=None,  # NULL for DMs
                status=SlackStatus.ENABLED
            )

            logger.info(f"Slack DM integration created for user {user_id}, workspace {workspace_id}")

            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(
                url=f"{frontend_url}/dashboard/channels/slack?success=true&show_channel_selection=true&workspace_id={workspace_id}"
            )

        except Exception as e:
            logger.error(f"Database error storing Slack integration: {e}")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(
                url=f"{frontend_url}/dashboard/channels/slack?error=database_error"
            )

    except Exception as e:
        logger.error(f"Unexpected error in OAuth callback: {e}")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(
            url=f"{frontend_url}/dashboard/channels/slack?error=unexpected_error"
        )


class SlackChannelSelection(BaseModel):
    """Selected Slack channel info."""
    channel_id: str
    channel_name: Optional[str] = None


class SlackAddChannelsRequest(BaseModel):
    """Request to add selected Slack channels."""
    workspace_id: str
    channels: list[SlackChannelSelection]


@router.get("/available-channels")
async def get_available_channels(
    workspace_id: Optional[str] = Query(None, description="Slack workspace ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get Slack channels created by the user that the bot can access.

    Uses the Slack user token to list channels and filters by creator.
    Intersects with bot-visible channels to ensure the bot can post.
    """
    try:
        dm_integration = await slack_service.get_dm_integration(db, current_user.id, workspace_id)
        if not dm_integration:
            return {
                "channels": [],
                "error": "no_integration",
                "message": "Please connect Slack first."
            }

        if not dm_integration.user_token or not dm_integration.slack_user_id:
            return {
                "channels": [],
                "error": "no_user_token",
                "message": "Please reconnect Slack to refresh your permissions."
            }

        # Channels created by the user (via user token)
        user_channels = await slack_consumer.get_user_channels(dm_integration.user_token)
        created_channel_ids = {
            ch.get("id")
            for ch in user_channels
            if ch.get("id") and ch.get("creator") == dm_integration.slack_user_id
        }

        if not created_channel_ids:
            return {
                "channels": [],
                "error": "no_created_channels",
                "message": "No channels created by you were found in this workspace."
            }

        # Channels the bot can access
        bot_channels = []
        if dm_integration.bot_user_id:
            bot_channels = await slack_consumer.get_bot_channels(
                dm_integration.bot_token,
                dm_integration.bot_user_id
            )

        bot_channel_map = {
            ch.get("id"): ch
            for ch in bot_channels
            if ch.get("id")
        }

        available = []
        for channel_id in created_channel_ids:
            channel = bot_channel_map.get(channel_id)
            if not channel:
                continue
            name = channel.get("name") or channel.get("name_normalized")
            if not name:
                continue
            available.append({
                "id": channel_id,
                "name": name,
                "is_private": bool(channel.get("is_private")),
            })

        if not available:
            return {
                "channels": [],
                "error": "bot_not_installed",
                "message": "The DRR bot is not a member of your created channels. Invite the bot to those channels and try again."
            }

        return {
            "workspace_id": dm_integration.workspace_id,
            "workspace_name": dm_integration.workspace_name,
            "channels": available
        }

    except SlackAPIError as e:
        logger.error(f"Failed to get available Slack channels: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Slack channels"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting Slack channels: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Slack channels"
        )


@router.post("/add-channels")
async def add_selected_channels(
    request: SlackAddChannelsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add selected Slack channels to user's integrations.
    """
    try:
        dm_integration = await slack_service.get_dm_integration(db, current_user.id, request.workspace_id)
        if not dm_integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Slack workspace integration found. Please connect Slack first."
            )

        added_count = 0
        failed_channels = []

        for channel in request.channels:
            try:
                await slack_service.create_channel_integration(
                    db=db,
                    workspace_integration=dm_integration,
                    channel_id=channel.channel_id,
                    channel_name=channel.channel_name
                )
                added_count += 1
            except Exception as e:
                logger.error(f"Failed to add Slack channel {channel.channel_id}: {e}")
                failed_channels.append(channel.channel_id)

        return {
            "success": True,
            "message": f"Added {added_count} channel integrations",
            "added_count": added_count,
            "failed_channels": failed_channels
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding selected Slack channels: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add selected channels"
        )


# Backward/alternate compatibility route: some environments configure
# SLACK_REDIRECT_URI without the "/oauth" segment (e.g. "/api/slack/callback").
# Expose an alias that forwards to the main handler so both
# /api/slack/oauth/callback and /api/slack/callback work.
@router.get("/callback")
async def oauth_callback_alias(
    code: str = Query(..., description="OAuth authorization code"),
    state: str = Query(..., description="CSRF protection state"),
    db: AsyncSession = Depends(get_db)
):
    return await oauth_callback(code=code, state=state, db=db)


def _verify_slack_signature(request: Request, body: bytes, signing_secret: str) -> bool:
    ts = request.headers.get("X-Slack-Request-Timestamp", "0")
    sig = request.headers.get("X-Slack-Signature", "")
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


@router.post("/events")
async def slack_events(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Slack Events API endpoint.

    - Verifies Slack signature using SLACK_SIGNING_SECRET
    - Handles url_verification
    - On member_joined_channel for our bot user, associates the channel with the integration
    """
    # Parse payload first to support Slack URL verification without blocking on signature
    raw_body = await request.body()
    try:
        logger.info(
            f"Slack events: received {len(raw_body)} bytes, headers x-slack-signature=%s, x-slack-request-timestamp=%s",
            request.headers.get("X-Slack-Signature"),
            request.headers.get("X-Slack-Request-Timestamp"),
        )
    except Exception:
        logger.exception("Slack events: failed to log headers")
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    # Verify signature for all requests including url_verification
    signing_secret = os.getenv("SLACK_SIGNING_SECRET")
    if not signing_secret:
        logger.error("Slack events: SLACK_SIGNING_SECRET not configured")
        return JSONResponse(status_code=500, content={"error": "Signing secret not configured"})

    if not _verify_slack_signature(request, raw_body, signing_secret):
        logger.warning("Slack events: invalid signature")
        return JSONResponse(status_code=401, content={"error": "Invalid signature"})

    # URL verification challenge (after signature is verified)
    if payload.get("type") == "url_verification":
        logger.info("Slack events: url_verification received, responding with challenge")
        return JSONResponse(content={"challenge": payload.get("challenge", "")})

    if payload.get("type") == "event_callback":
        event = payload.get("event", {})
        team_id = payload.get("team_id") or event.get("team")
        event_type = event.get("type")
        logger.info("Slack events: event_callback type=%s team_id=%s", event_type, team_id)
        if event_type == "member_joined_channel":
            bot_user = event.get("user")
            channel_id = event.get("channel")
            logger.info("Slack events: member_joined_channel user=%s channel=%s", bot_user, channel_id)

            if team_id and bot_user and channel_id:
                # Find existing workspace integrations (DMs) for this workspace/bot
                integrations = await slack_service.get_by_workspace_and_bot_user(db, team_id, bot_user)
                logger.info("Slack events: matched %d integration(s) for workspace/bot", len(integrations))

                # Create a new integration for this channel based on the first workspace integration
                if integrations:
                    base_integration = integrations[0]  # Use any existing integration as template

                    # Fetch channel info to get the channel name
                    channel_name = None
                    try:
                        channel_info = await slack_consumer.get_channel_info(base_integration.bot_token, channel_id)
                        channel_name = channel_info.get("name") or channel_info.get("name_normalized")
                        logger.info("Slack events: channel name=%s", channel_name)
                    except Exception as e:
                        logger.warning(f"Failed to get channel name for {channel_id}: {e}")

                    # Create new channel integration
                    try:
                        await slack_service.create_channel_integration(
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


@router.get("/integrations", response_model=list[SlackRead])
async def get_integrations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all Slack integrations for the current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of Slack integrations
    """
    try:
        integrations = await slack_service.get_by_user(db, current_user.id)
        return integrations

    except Exception as e:
        logger.error(f"Error getting Slack integrations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Slack integrations"
        )


@router.post("/integrations/{integration_id}/test", response_model=TestConnectionResponse)
async def test_connection(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    verify_token: Optional[str] = Query(None, description="Optional small token generated by frontend for client-side verification")
):
    """
    Send a test message to verify Slack connection.

    Args:
        integration_id: Slack integration ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Test connection result
    """
    try:
        # Get integration
        integration = await slack_service.get_by_id(db, integration_id)

        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slack integration not found"
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
                verification_url = f"{frontend}/dashboard/channels/slack?verified={verify_token}&integration_id={integration.id}"
            else:
                # Fallback to signed server token (more secure) as a robust option
                payload = {
                    "purpose": "slack_verify",
                    "integration_id": integration.id,
                    "user_id": str(current_user.id),
                    "exp": datetime.now(timezone.utc) + timedelta(days=7),
                }
                signed = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
                redirect_uri = os.getenv("SLACK_REDIRECT_URI", "")
                parsed = urlparse(redirect_uri)
                base = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else os.getenv("FRONTEND_URL", "http://localhost:3000")
                verification_url = f"{base}/api/slack/verify?token={signed}"
        except Exception:
            logger.exception("Failed to build Slack verification URL; continuing without it")
            verification_url = None

        # Send test message
        try:
            # Check if this is a DM or channel integration
            is_dm = integration.channel_id == integration.slack_user_id

            if is_dm:
                # Send test message to DM
                await slack_consumer.send_test_message(
                    access_token=integration.bot_token,
                    user_id=integration.slack_user_id,
                    verification_url=verification_url
                )
                logger.info(f"Test DM sent successfully for integration {integration_id}")
                message = "Test message sent to your Slack DM. Please click '✅ Confirm in DRR' to activate."
            else:
                # Send test message to channel
                channel_name_display = f"#{integration.channel_name}" if integration.channel_name else integration.channel_id
                await slack_consumer.send_message(
                    access_token=integration.bot_token,
                    channel_id=integration.channel_id,
                    text=f"✅ DRR test: channel {channel_name_display} is connected and ready to receive notifications.",
                )
                logger.info(f"Test message sent to channel {integration.channel_id} for integration {integration_id}")
                message = f"Test message sent to {channel_name_display}. Check Slack to confirm."

            return TestConnectionResponse(
                success=True,
                message=message
            )

        except SlackAPIError as e:
            logger.error(f"Failed to send test message: {e}")
            return TestConnectionResponse(
                success=False,
                message=f"Failed to send test message: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error testing Slack connection: {e}")
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
    Delete a Slack integration.

    Args:
        integration_id: Slack integration ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message
    """
    try:
        # Get integration
        integration = await slack_service.get_by_id(db, integration_id)

        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slack integration not found"
            )

        # Verify ownership
        if integration.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this integration"
            )

        # Attempt to uninstall the app from Slack (best-effort)
        try:
            if integration.bot_token:
                uninstalled = await slack_consumer.uninstall_app(integration.bot_token)
                if not uninstalled:
                    await slack_consumer.revoke_token(integration.bot_token)
        except Exception as e:
            logger.warning(f"Unable to uninstall or revoke Slack app for integration {integration_id}: {e}")

        # Delete integration from our DB
        deleted = await slack_service.delete(db, integration_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete integration"
            )

        logger.info(f"Deleted Slack integration {integration_id}")

        return {"message": "Integration deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Slack integration: {e}")
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
    Activate a Slack integration after client-side verification.

    Security: relies on standard JWT auth and ownership check; client-side "verified" token
    is validated in the browser before this call.
    """
    try:
        integration = await slack_service.get_by_id(db, integration_id)
        if not integration:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slack integration not found")
        if integration.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this integration")

        updated = await slack_service.update_status(db, integration_id, SlackStatus.ACTIVE)
        if not updated:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update status")

        return TestConnectionResponse(success=True, message="Integration verified and activated.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating Slack integration: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to activate integration")


@router.get("/verify")
async def verify_slack_integration(
    token: str = Query(..., description="Signed verification token"),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify Slack DM is working via a signed link included in the test message.

    Decodes the signed token, validates intent, updates the integration status
    to ACTIVE, and redirects to the frontend with a success indicator.
    """
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if data.get("purpose") != "slack_verify":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

        integration_id = data.get("integration_id")
        user_id = data.get("user_id")
        if not integration_id or not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token data")

        # Load integration and ensure it matches the token
        integration = await slack_service.get_by_id(db, int(integration_id))
        if not integration:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")
        if str(integration.user_id) != str(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token user mismatch")

        # Update status to ACTIVE and only show success on actual update
        updated = await slack_service.update_status(db, int(integration_id), SlackStatus.ACTIVE)
        logger.info(f"Slack integration {integration_id} verified via link click; updated={bool(updated)}")

        if updated:
            return RedirectResponse(url=f"{frontend_url}/dashboard/channels/slack?verified=true")
        return RedirectResponse(url=f"{frontend_url}/dashboard/channels/slack?error=verify_failed")

    except JWTError:
        return RedirectResponse(url=f"{frontend_url}/dashboard/channels/slack?error=verify_failed")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error verifying Slack integration")
        return RedirectResponse(url=f"{frontend_url}/dashboard/channels/slack?error=verify_failed")
