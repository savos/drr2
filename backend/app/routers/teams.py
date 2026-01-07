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

    try:
        user_teams = await teams_consumer.get_user_teams(dm_integration.access_token)
    except TeamsAPIError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to fetch teams from Microsoft Teams")

    available_teams: List[TeamInfo] = []
    for team in user_teams:
        team_id = team.get("id")
        team_name = team.get("displayName")
        if not team_id or not team_name:
            continue
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
async def bot_webhook(request: Request):
    """
    Placeholder endpoint for Teams Bot Framework webhook.
    To implement: wire up Bot Framework Adapter, handle conversationUpdate
    to capture conversation references for personal and team scope.
    """
    return JSONResponse({"detail": "Teams bot webhook not implemented"}, status_code=501)
