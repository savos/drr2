"""Teams router for OAuth integration and channel management."""
import os
import uuid
import logging
from typing import Optional, List
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database.database import get_db
from app.models.users import User
from app.models.teams import TeamsStatus
from app.schemas.teams import TeamsRead, ChannelSelection, AddChannelsRequest
from app.utils.security import get_current_user
from app.consumers.teams import TeamsConsumer, TeamsAPIError
from app.services.teams import TeamsService
from app.services.teams_conversation import TeamsConversationService
from app.utils.botframework_jwt import verify_bot_jwt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/teams", tags=["teams"])

# Initialize Teams consumer
teams_consumer = TeamsConsumer()
teams_service = TeamsService()


# Request/Response Models
class OAuthUrlResponse(BaseModel):
    """OAuth URL response."""
    oauth_url: str
    state: str


class TeamInfo(BaseModel):
    """Team information for frontend."""
    id: str
    name: str
    description: Optional[str] = None
    channels: List[dict] = []


class AvailableTeamsResponse(BaseModel):
    """Available teams response."""
    teams: List[TeamInfo]


class AddChannelsResponse(BaseModel):
    """Response after adding channels."""
    success: bool
    added_count: int
    integrations: List[TeamsRead]


class TeamsStatusResponse(BaseModel):
    """Status of Teams app installation for the user."""
    personal_installed: bool
    personal_deeplink: Optional[str] = None


class InstallTargets(BaseModel):
    """Targets to install the Teams app to."""
    include_personal: bool = True
    team_ids: List[str] = []


class InstallResult(BaseModel):
    """Result of installation attempts."""
    personal: Optional[Dict[str, Any]] = None
    teams: Dict[str, Dict[str, Any]] = {}


class SendChannelTestRequest(BaseModel):
    team_id: str
    channel_id: str
    message: Optional[str] = None


class SendDMTestRequest(BaseModel):
    message: Optional[str] = None


@router.get("/oauth/url", response_model=OAuthUrlResponse)
async def get_oauth_url(
    current_user: User = Depends(get_current_user)
):
    """
    Get Microsoft Teams OAuth authorization URL.

    Generates a unique state parameter for CSRF protection and returns
    the Teams OAuth URL for user authorization.

    Args:
        current_user: Current authenticated user

    Returns:
        OAuth URL and state parameter
    """
    try:
        # Generate unique state for CSRF protection
        state = f"{current_user.id}:{uuid.uuid4()}"

        # Get OAuth URL
        oauth_url = teams_consumer.get_oauth_url(state)

        logger.info(f"Generated Teams OAuth URL for user {current_user.id}")

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


@router.get("/status", response_model=TeamsStatusResponse)
async def get_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personal-scope install status and deep link for adding the app.
    """
    dm_integration = await teams_service.get_first_by_user(db, current_user.id)
    if not dm_integration or not dm_integration.access_token or not dm_integration.teams_user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Teams connection found. Connect first.")

    installed = await teams_consumer.is_app_installed_for_user(
        dm_integration.access_token, dm_integration.teams_user_id
    )
    deeplink = teams_consumer.deep_link_add_personal()
    return TeamsStatusResponse(personal_installed=installed, personal_deeplink=deeplink)


@router.get("/oauth/callback")
async def oauth_callback(
    code: str = Query(..., description="OAuth authorization code"),
    state: str = Query(..., description="CSRF protection state"),
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Microsoft Teams OAuth callback.

    Exchanges the authorization code for an access token and stores
    the Teams integration in the database.

    Args:
        code: OAuth authorization code from Microsoft
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
                url=f"{frontend_url}/dashboard/channels/teams?error=invalid_state"
            )

        # Exchange code for token
        try:
            oauth_data = await teams_consumer.exchange_code_for_token(code)
        except TeamsAPIError as e:
            logger.error(f"OAuth token exchange failed: {e}")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(
                url=f"{frontend_url}/dashboard/channels/teams?error=oauth_failed"
            )

        # Extract tokens
        access_token = oauth_data.get("access_token")
        refresh_token = oauth_data.get("refresh_token")
        token_expires_at = oauth_data.get("token_expires_at")

        if not access_token:
            logger.error("Teams OAuth missing access_token")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(
                url=f"{frontend_url}/dashboard/channels/teams?error=missing_data"
            )

        # Get current user from Microsoft Graph
        try:
            me = await teams_consumer.get_current_user(access_token)
        except TeamsAPIError as e:
            logger.error(f"Failed to get Teams user: {e}")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(
                url=f"{frontend_url}/dashboard/channels/teams?error=oauth_failed"
            )

        teams_user_id = me.get("id")
        email = me.get("userPrincipalName") or me.get("mail")
        username = me.get("displayName")

        if not teams_user_id:
            logger.error("Teams user id missing in /me")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(
                url=f"{frontend_url}/dashboard/channels/teams?error=missing_data"
            )

        # Store DM integration (base integration with tokens)
        try:
            dm_integration = await teams_service.create_teams_integration(
                db=db,
                user_id=user_id,
                teams_user_id=teams_user_id,
                email=email,
                username=username,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=token_expires_at,
                team_id=None,
                team_name=None,
                channel_id=None,
                channel_name=None,
                status=TeamsStatus.ENABLED
            )

            logger.info(f"Teams DM integration created for user {user_id}")

            # Redirect to frontend with team selection modal
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(
                url=f"{frontend_url}/dashboard/channels/teams?success=true&show_team_selection=true"
            )

        except Exception as e:
            logger.error(f"Database error storing Teams integration: {e}")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(
                url=f"{frontend_url}/dashboard/channels/teams?error=database_error"
            )

    except Exception as e:
        logger.error(f"Unexpected error in OAuth callback: {e}")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(
            url=f"{frontend_url}/dashboard/channels/teams?error=unexpected_error"
        )


@router.get("/integrations", response_model=List[TeamsRead])
async def get_integrations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all Teams integrations for the current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of Teams integrations
    """
    try:
        integrations = await teams_service.get_by_user(db, current_user.id)
        return integrations

    except Exception as e:
        logger.error(f"Error getting Teams integrations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get integrations"
        )


@router.get("/available-teams", response_model=AvailableTeamsResponse)
async def get_available_teams(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get available Teams teams and channels for integration.

    Returns teams with their channels that the user can integrate with DRR.
    Filters out already integrated channels.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of teams with available channels
    """
    try:
        # Get user's DM integration (base integration with tokens)
        dm_integration = await teams_service.get_first_by_user(db, current_user.id)

        if not dm_integration or not dm_integration.access_token:
            logger.error(f"No Teams integration found for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Teams connection found. Please connect Teams first."
            )

        # Get existing integrations to filter out already connected channels
        existing_integrations = await teams_service.get_by_user(db, current_user.id)
        existing_channel_keys = {
            f"{integ.team_id}:{integ.channel_id}"
            for integ in existing_integrations
            if integ.team_id and integ.channel_id
        }

        # Get user's teams
        try:
            user_teams = await teams_consumer.get_user_teams(dm_integration.access_token)
        except TeamsAPIError as e:
            logger.error(f"Failed to get Teams teams: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch teams from Microsoft Teams"
            )

        # Get channels for each team
        available_teams = []
        for team in user_teams:
            team_id = team.get("id")
            team_name = team.get("displayName")

            if not team_id or not team_name:
                continue

            try:
                channels = await teams_consumer.get_team_channels(
                    dm_integration.access_token,
                    team_id
                )

                # Filter out already integrated channels
                available_channels = []
                for channel in channels:
                    channel_id = channel.get("id")
                    channel_name = channel.get("displayName")
                    channel_type = channel.get("membershipType", "standard")

                    if not channel_id or not channel_name:
                        continue

                    # Skip if already integrated
                    channel_key = f"{team_id}:{channel_id}"
                    if channel_key in existing_channel_keys:
                        continue

                    available_channels.append({
                        "id": channel_id,
                        "name": channel_name,
                        "type": channel_type
                    })

                if available_channels:
                    available_teams.append(TeamInfo(
                        id=team_id,
                        name=team_name,
                        description=team.get("description"),
                        channels=available_channels
                    ))

            except TeamsAPIError as e:
                logger.warning(f"Failed to get channels for team {team_id}: {e}")
                continue

        logger.info(f"Found {len(available_teams)} teams with available channels for user {current_user.id}")

        return AvailableTeamsResponse(teams=available_teams)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting available teams: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available teams"
        )


@router.get("/owned-teams", response_model=AvailableTeamsResponse)
async def get_owned_teams(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get only teams where current user is an owner, with their channels,
    excluding already integrated channels.
    """
    dm_integration = await teams_service.get_first_by_user(db, current_user.id)
    if not dm_integration or not dm_integration.access_token or not dm_integration.teams_user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Teams connection found. Connect first.")

    existing_integrations = await teams_service.get_by_user(db, current_user.id)
    existing_channel_keys = {
        f"{integ.team_id}:{integ.channel_id}"
        for integ in existing_integrations
        if integ.team_id and integ.channel_id
    }

    # Prefer Graph ownedObjects for owned teams
    user_owned = await teams_consumer.get_owned_teams(dm_integration.access_token)

    # Fallback to joinedTeams + owner role check if ownedObjects returned nothing
    teams_source = user_owned
    owner_checked = True
    if not teams_source:
        try:
            teams_source = await teams_consumer.get_user_teams(dm_integration.access_token)
            owner_checked = False
        except TeamsAPIError:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to fetch teams from Microsoft Teams")

    available_teams: List[TeamInfo] = []
    for team in teams_source:
        team_id = team.get("id")
        team_name = team.get("displayName")
        if not team_id or not team_name:
            continue
        if not owner_checked:
            is_owner = await teams_consumer.is_user_owner_of_team(
                dm_integration.access_token, team_id, dm_integration.teams_user_id
            )
            if not is_owner:
                continue
        try:
            channels = await teams_consumer.get_team_channels(dm_integration.access_token, team_id)
        except TeamsAPIError:
            continue
        available_channels = []
        for ch in channels:
            cid = ch.get("id")
            cname = ch.get("displayName")
            ctype = ch.get("membershipType", "standard")
            if not cid or not cname:
                continue
            key = f"{team_id}:{cid}"
            if key in existing_channel_keys:
                continue
            available_channels.append({"id": cid, "name": cname, "type": ctype})
        if available_channels:
            available_teams.append(
                TeamInfo(id=team_id, name=team_name, description=team.get("description"), channels=available_channels)
            )

    return AvailableTeamsResponse(teams=available_teams)


@router.post("/install", response_model=InstallResult)
async def install_app(
    targets: InstallTargets,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Try to install the Teams app for the user (personal) and selected team IDs.
    Returns per-target results and deep links for fallback if needed.
    """
    dm_integration = await teams_service.get_first_by_user(db, current_user.id)
    if not dm_integration or not dm_integration.access_token or not dm_integration.teams_user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Teams connection found. Connect first.")

    results: InstallResult = InstallResult(personal=None, teams={})

    if targets.include_personal:
        installed = await teams_consumer.is_app_installed_for_user(
            dm_integration.access_token, dm_integration.teams_user_id
        )
        if installed:
            results.personal = {"installed": True}
        else:
            ok = await teams_consumer.install_app_for_user(
                dm_integration.access_token, dm_integration.teams_user_id
            )
            if ok:
                results.personal = {"installed": True}
            else:
                results.personal = {
                    "installed": False,
                    "deeplink": teams_consumer.deep_link_add_personal(),
                    "hint": "Click the deep link to add the app to your Teams."
                }

    for team_id in targets.team_ids:
        team_res: Dict[str, Any] = {"teamId": team_id}
        already = await teams_consumer.is_app_installed_for_team(
            dm_integration.access_token, team_id
        )
        if already:
            team_res.update({"installed": True})
        else:
            ok = await teams_consumer.install_app_for_team(
                dm_integration.access_token, team_id
            )
            if ok:
                team_res.update({"installed": True})
            else:
                team_res.update({
                    "installed": False,
                    "deeplink": teams_consumer.deep_link_add_to_team(team_id),
                    "hint": "Use the deep link to add the app to this team. You may need to be a team owner."
                })
        results.teams[team_id] = team_res

    return results


@router.post("/send-test-channel")
async def send_test_channel(
    payload: SendChannelTestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a test message to a specific team channel using Graph (appears as the user).
    This is a connectivity test until bot messaging is fully wired.
    """
    dm_integration = await teams_service.get_first_by_user(db, current_user.id)
    if not dm_integration or not dm_integration.access_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Teams connection found. Connect first.")

    message = payload.message or "DRR: This is a test message to your Teams channel."
    try:
        await teams_consumer.send_channel_message(
            dm_integration.access_token,
            payload.team_id,
            payload.channel_id,
            message,
        )
        return {"ok": True}
    except TeamsAPIError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.post("/send-test-dm")
async def send_test_dm(
    payload: SendDMTestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a test DM via Bot Framework if a conversation reference is stored.
    Steps for the user if not ready:
      1) Install DRR app in Teams (deep link),
      2) Send a message to the DRR app (to create conversation),
      3) Retry.
    """
    # Find base integration
    dm_integration = await teams_service.get_first_by_user(db, current_user.id)
    if not dm_integration:
        raise HTTPException(status_code=404, detail="No Teams connection found. Connect first.")

    # Look up stored personal conversation
    conv_row = await TeamsConversationService.get_personal_by_user(db, current_user.id)
    if not conv_row or not conv_row.conversation_id or not conv_row.service_url:
        deeplink = teams_consumer.deep_link_add_personal()
        return JSONResponse(
            status_code=409,
            content={
                "detail": "Open the DRR app in Teams and send any message so we can capture your DM conversation.",
                "deeplink": deeplink,
            },
        )

    text = payload.message or "DRR: This is a test DM from your DRR bot."
    ok = await teams_consumer.send_bot_dm(
        service_url=conv_row.service_url,
        conversation_id=conv_row.conversation_id,
        text=text,
    )
    if not ok:
        raise HTTPException(status_code=502, detail="Failed to send DM. Check bot credentials and app installation.")
    return {"ok": True}


@router.post("/add-channels", response_model=AddChannelsResponse)
async def add_selected_channels(
    request: AddChannelsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add selected Teams channels as integrations.

    Creates new integrations for each selected channel using the base
    integration's access tokens.

    Args:
        request: List of selected channels
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success status and list of created integrations
    """
    try:
        # Get user's DM integration (base integration with tokens)
        dm_integration = await teams_service.get_first_by_user(db, current_user.id)

        if not dm_integration:
            logger.error(f"No Teams DM integration found for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Teams connection found. Please connect Teams first."
            )

        # Create integrations for each selected channel
        created_integrations = []
        for channel_selection in request.channels:
            try:
                integration = await teams_service.create_channel_integration(
                    db=db,
                    base_integration=dm_integration,
                    team_id=channel_selection.team_id,
                    team_name=channel_selection.team_name,
                    channel_id=channel_selection.channel_id,
                    channel_name=channel_selection.channel_name
                )
                created_integrations.append(integration)
                logger.info(
                    f"Created Teams channel integration for user {current_user.id}: "
                    f"{channel_selection.team_name} / {channel_selection.channel_name}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to create integration for channel {channel_selection.channel_id}: {e}"
                )
                continue

        return AddChannelsResponse(
            success=True,
            added_count=len(created_integrations),
            integrations=created_integrations
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding Teams channels: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add selected channels"
        )


@router.delete("/integrations/{integration_id}")
async def delete_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a Teams integration.

    Args:
        integration_id: Integration ID to delete
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message
    """
    try:
        # Get integration
        integration = await teams_service.get_by_id(db, integration_id)

        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )

        # Verify ownership
        if integration.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this integration"
            )

        # Delete integration
        success = await teams_service.delete(db, integration_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete integration"
            )

        logger.info(f"Deleted Teams integration {integration_id} for user {current_user.id}")

        return {"success": True, "message": "Integration deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Teams integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete integration"
        )


@router.post("/bot")
async def bot_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Minimal Teams bot webhook to capture conversation references.
    Note: In dev, this does not validate JWT signatures. Use only in dev.
    Stores a DM conversation ref in Teams table for the matched user.
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"detail": "Invalid JSON"}, status_code=400)

    activity_type = body.get("type")
    service_url = body.get("serviceUrl")
    conversation = (body.get("conversation") or {})
    conversation_id = conversation.get("id")
    from_obj = body.get("from") or {}
    # Prefer aadObjectId if provided
    aad_id = from_obj.get("aadObjectId") or from_obj.get("id")
    channel_data = body.get("channelData") or {}
    conv_type = (conversation.get("conversationType") or "").lower()
    team_info = (channel_data.get("team") or {})
    channel_info = (channel_data.get("channel") or {})
    team_id = team_info.get("id")
    channel_id = channel_info.get("id")

    if not (service_url and conversation_id and aad_id):
        return JSONResponse({"detail": "Missing fields in activity"}, status_code=200)

    # Validate Bot Framework token — mandatory
    auth_header = request.headers.get("Authorization")
    bot_app_id = os.getenv("BOT_APP_ID") or os.getenv("MICROSOFT_APP_ID")
    if not bot_app_id:
        logger.error("Bot webhook received but BOT_APP_ID / MICROSOFT_APP_ID is not configured")
        return JSONResponse({"detail": "Bot authentication not configured"}, status_code=503)

    channel_service = os.getenv("BOT_CHANNEL_SERVICE", "public").lower()
    try:
        await verify_bot_jwt(
            auth_header,
            audience=bot_app_id,
            expected_service_url=service_url,
            channel_service=channel_service,
        )
    except Exception as e:
        logger.warning(f"Bot JWT validation failed: {e}")
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)

    # Find any integration row matching this Teams user id
    integ = await teams_service.get_any_by_teams_user_id(db, aad_id)
    if not integ:
        # Could not match to an app user yet; ignore silently
        return JSONResponse({"detail": "No matching user for Teams activity"}, status_code=200)

    # Store conversation reference (DM or team channel)
    if conv_type == "channel" and team_id and channel_id:
        saved = await TeamsConversationService.upsert_team(
            db=db,
            user_id=integ.user_id,
            service_url=service_url,
            conversation_id=conversation_id,
            team_id=team_id,
            channel_id=channel_id,
        )
    else:
        saved = await TeamsConversationService.upsert_personal(
            db=db,
            user_id=integ.user_id,
            service_url=service_url,
            conversation_id=conversation_id,
        )
    if not saved:
        logger.error("Failed to persist DM conversation ref")

    return JSONResponse({"detail": "ok"}, status_code=200)
