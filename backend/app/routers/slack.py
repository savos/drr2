"""Slack router for OAuth integration and messaging."""
import os
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse
from datetime import datetime, timedelta
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

        if not all([access_token, workspace_id]):
            logger.error("Missing required OAuth data")
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(
                url=f"{frontend_url}/dashboard/channels/slack?error=missing_data"
            )

        # Store integration in database
        try:
            await slack_service.create_slack_integration(
                db=db,
                user_id=user_id,
                workspace_id=workspace_id,
                workspace_name=workspace_name,
                access_token=access_token,
                bot_user_id=bot_user_id,
                slack_user_id=slack_user_id,
                status=SlackStatus.ENABLED
            )

            logger.info(f"Slack integration created for user {user_id}, workspace {workspace_id}")

            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            return RedirectResponse(
                url=f"{frontend_url}/dashboard/channels/slack?success=true"
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
                    "exp": datetime.utcnow() + timedelta(days=7),
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
            await slack_consumer.send_test_message(
                access_token=integration.bot_token,
                user_id=integration.slack_user_id,
                verification_url=verification_url
            )

            # Do NOT set Active on test; only after user confirms via Slack link
            logger.info(f"Test message sent successfully for integration {integration_id}")

            return TestConnectionResponse(
                success=True,
                message="Test message sent. Please click '✅ Confirm in DRR' in your Slack DM."
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
