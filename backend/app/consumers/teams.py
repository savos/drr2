"""Microsoft Teams API consumer for communicating with Microsoft Graph API."""
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import httpx

logger = logging.getLogger(__name__)


class TeamsAPIError(Exception):
    """Custom exception for Teams API errors."""
    pass


class TeamsConsumer:
    """Microsoft Teams API consumer for messaging and channel operations."""

    def __init__(self):
        """Initialize Teams consumer with OAuth credentials."""
        self.client_id = os.getenv("TEAMS_CLIENT_ID")
        self.client_secret = os.getenv("TEAMS_CLIENT_SECRET")
        self.redirect_uri = os.getenv("TEAMS_REDIRECT_URI")
        self.tenant_id = os.getenv("TEAMS_TENANT_ID", "common")  # 'common' for multi-tenant

        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            logger.warning("Teams OAuth credentials not fully configured")

        self.graph_base = "https://graph.microsoft.com/v1.0"
        self.auth_base = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0"

    def get_oauth_url(self, state: str) -> str:
        """Get Microsoft Teams OAuth2 authorization URL."""
        # Scopes for reading user info, teams, channels, and sending messages
        scopes = "User.Read Team.ReadBasic.All Channel.ReadBasic.All Chat.ReadBasic offline_access"

        return (
            f"{self.auth_base}/authorize"
            f"?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code"
            f"&scope={scopes}"
            f"&state={state}"
            f"&response_mode=query"
        )

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange OAuth2 authorization code for access token."""
        async with httpx.AsyncClient() as client:
            try:
                data = {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                    "scope": "User.Read Team.ReadBasic.All Channel.ReadBasic.All Chat.ReadBasic offline_access"
                }

                response = await client.post(
                    f"{self.auth_base}/token",
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10.0
                )

                if response.status_code != 200:
                    error_data = response.json() if response.text else {}
                    error_msg = error_data.get("error_description", "Token exchange failed")
                    logger.error(f"Teams OAuth token exchange failed: {error_msg}")
                    raise TeamsAPIError(f"Token exchange failed: {error_msg}")

                token_data = response.json()

                # Calculate token expiration
                if "expires_in" in token_data:
                    token_data["token_expires_at"] = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])

                return token_data

            except httpx.HTTPError as e:
                logger.error(f"HTTP error during Teams token exchange: {e}")
                raise TeamsAPIError(f"HTTP error: {str(e)}")

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an expired access token using refresh token."""
        async with httpx.AsyncClient() as client:
            try:
                data = {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "scope": "User.Read Team.ReadBasic.All Channel.ReadBasic.All Chat.ReadBasic offline_access"
                }

                response = await client.post(
                    f"{self.auth_base}/token",
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10.0
                )

                if response.status_code != 200:
                    error_data = response.json() if response.text else {}
                    error_msg = error_data.get("error_description", "Token refresh failed")
                    logger.error(f"Teams token refresh failed: {error_msg}")
                    raise TeamsAPIError(f"Token refresh failed: {error_msg}")

                token_data = response.json()

                # Calculate token expiration
                if "expires_in" in token_data:
                    token_data["token_expires_at"] = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])

                return token_data

            except httpx.HTTPError as e:
                logger.error(f"HTTP error during Teams token refresh: {e}")
                raise TeamsAPIError(f"HTTP error: {str(e)}")

    async def get_current_user(self, access_token: str) -> Dict[str, Any]:
        """Get current user information using OAuth2 access token."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.graph_base}/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )

                if response.status_code != 200:
                    error_msg = f"Get user failed with status {response.status_code}"
                    logger.error(f"Teams API error getting user: {error_msg}")
                    raise TeamsAPIError(error_msg)

                return response.json()

            except httpx.HTTPError as e:
                logger.error(f"HTTP error getting Teams user: {e}")
                raise TeamsAPIError(f"HTTP error: {str(e)}")

    async def get_user_teams(self, access_token: str) -> list[Dict[str, Any]]:
        """Get teams that the user is a member of."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.graph_base}/me/joinedTeams",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )

                if response.status_code != 200:
                    error_msg = f"Get teams failed with status {response.status_code}"
                    logger.error(f"Teams API error getting teams: {error_msg}")
                    raise TeamsAPIError(error_msg)

                data = response.json()
                return data.get("value", [])

            except httpx.HTTPError as e:
                logger.error(f"HTTP error getting Teams teams: {e}")
                raise TeamsAPIError(f"HTTP error: {str(e)}")

    async def get_team_channels(self, access_token: str, team_id: str) -> list[Dict[str, Any]]:
        """Get channels for a specific team."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.graph_base}/teams/{team_id}/channels",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )

                if response.status_code != 200:
                    error_msg = f"Get channels failed with status {response.status_code}"
                    logger.error(f"Teams API error getting channels for team {team_id}: {error_msg}")
                    raise TeamsAPIError(error_msg)

                data = response.json()
                return data.get("value", [])

            except httpx.HTTPError as e:
                logger.error(f"HTTP error getting Teams channels: {e}")
                raise TeamsAPIError(f"HTTP error: {str(e)}")

    async def send_channel_message(
        self,
        access_token: str,
        team_id: str,
        channel_id: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Send a message to a Teams channel.
        Note: This requires ChatMessage.Send permission and may need app permissions.
        """
        async with httpx.AsyncClient() as client:
            try:
                message_data = {
                    "body": {
                        "content": content,
                        "contentType": "text"
                    }
                }

                response = await client.post(
                    f"{self.graph_base}/teams/{team_id}/channels/{channel_id}/messages",
                    json=message_data,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    timeout=10.0
                )

                if response.status_code not in [200, 201]:
                    error_data = response.json() if response.text else {}
                    error_msg = error_data.get("error", {}).get("message", "Send message failed")
                    logger.error(f"Teams API error sending message: {error_msg}")
                    raise TeamsAPIError(f"Send message failed: {error_msg}")

                return response.json()

            except httpx.HTTPError as e:
                logger.error(f"HTTP error sending Teams message: {e}")
                raise TeamsAPIError(f"HTTP error: {str(e)}")
