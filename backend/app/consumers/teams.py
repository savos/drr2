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
        self.teams_app_id = os.getenv("TEAMS_APP_ID")  # Teams app (manifest) ID for installs/deep links

    def get_oauth_url(self, state: str) -> str:
        """Get Microsoft Teams OAuth2 authorization URL."""
        # Scopes for user info, teams, channels, members, and app installs
        scopes = " ".join([
            "openid", "profile", "email", "offline_access", "User.Read",
            "Team.ReadBasic.All", "Channel.ReadBasic.All", "TeamMember.Read.All",
            "TeamsAppInstallation.ReadWriteForUser", "TeamsAppInstallation.ReadWriteForTeam",
        ])

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
                    "scope": " ".join([
                        "openid", "profile", "email", "offline_access", "User.Read",
                        "Team.ReadBasic.All", "Channel.ReadBasic.All", "TeamMember.Read.All",
                        "TeamsAppInstallation.ReadWriteForUser", "TeamsAppInstallation.ReadWriteForTeam",
                    ])
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
                    "scope": " ".join([
                        "openid", "profile", "email", "offline_access", "User.Read",
                        "Team.ReadBasic.All", "Channel.ReadBasic.All", "TeamMember.Read.All",
                        "TeamsAppInstallation.ReadWriteForUser", "TeamsAppInstallation.ReadWriteForTeam",
                    ])
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

    async def is_user_owner_of_team(self, access_token: str, team_id: str, user_id: str) -> bool:
        """Check if given user is an owner of the team by inspecting member roles."""
        async with httpx.AsyncClient() as client:
            try:
                # List team members and filter for owners
                resp = await client.get(
                    f"{self.graph_base}/teams/{team_id}/members",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0,
                )
                if resp.status_code != 200:
                    logger.warning(
                        f"Failed to get team members for {team_id}: {resp.status_code}"
                    )
                    return False
                members = resp.json().get("value", [])
                for m in members:
                    roles = m.get("roles", []) or []
                    # user IDs may be under 'userId' for AAD users
                    mid = m.get("userId") or m.get("id")
                    if mid == user_id and any(r.lower() == "owner" for r in roles):
                        return True
                return False
            except httpx.HTTPError as e:
                logger.error(f"HTTP error getting team members: {e}")
                return False

    async def list_user_installed_apps(self, access_token: str, user_id: str) -> list[Dict[str, Any]]:
        """List Teams apps installed for the user (personal scope)."""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.graph_base}/users/{user_id}/teamwork/installedApps?$expand=teamsApp",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0,
                )
                if resp.status_code != 200:
                    logger.warning(
                        f"Failed to list user installed apps: {resp.status_code} {resp.text}"
                    )
                    return []
                return resp.json().get("value", [])
            except httpx.HTTPError as e:
                logger.error(f"HTTP error listing user installed apps: {e}")
                return []

    async def is_app_installed_for_user(self, access_token: str, user_id: str) -> bool:
        """Check if our Teams app is installed for the user (personal)."""
        if not self.teams_app_id:
            logger.warning("TEAMS_APP_ID is not configured; cannot check install status")
            return False
        apps = await self.list_user_installed_apps(access_token, user_id)
        for app in apps:
            teams_app = app.get("teamsApp") or {}
            if teams_app.get("id") == self.teams_app_id:
                return True
        return False

    async def install_app_for_user(self, access_token: str, user_id: str) -> bool:
        """Install our Teams app for the user (personal scope). Requires delegated permission."""
        if not self.teams_app_id:
            raise TeamsAPIError("TEAMS_APP_ID is not configured")
        payload = {
            "teamsApp@odata.bind": f"https://graph.microsoft.com/v1.0/appCatalogs/teamsApps/{self.teams_app_id}"
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.graph_base}/users/{user_id}/teamwork/installedApps",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    timeout=10.0,
                )
                if resp.status_code in (200, 201):
                    return True
                logger.warning(f"Failed to install app for user: {resp.status_code} {resp.text}")
                return False
            except httpx.HTTPError as e:
                logger.error(f"HTTP error installing app for user: {e}")
                return False

    async def is_app_installed_for_team(self, access_token: str, team_id: str) -> bool:
        """Check if our Teams app is installed in a team."""
        if not self.teams_app_id:
            logger.warning("TEAMS_APP_ID is not configured; cannot check team install")
            return False
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.graph_base}/teams/{team_id}/installedApps?$expand=teamsApp",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0,
                )
                if resp.status_code != 200:
                    logger.warning(f"Failed to list team installed apps: {resp.status_code} {resp.text}")
                    return False
                for item in resp.json().get("value", []):
                    teams_app = item.get("teamsApp") or {}
                    if teams_app.get("id") == self.teams_app_id:
                        return True
                return False
            except httpx.HTTPError as e:
                logger.error(f"HTTP error listing team installed apps: {e}")
                return False

    async def install_app_for_team(self, access_token: str, team_id: str) -> bool:
        """Install our Teams app in a specific team (requires owner + delegated permission)."""
        if not self.teams_app_id:
            raise TeamsAPIError("TEAMS_APP_ID is not configured")
        payload = {
            "teamsApp@odata.bind": f"https://graph.microsoft.com/v1.0/appCatalogs/teamsApps/{self.teams_app_id}"
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.graph_base}/teams/{team_id}/installedApps",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    timeout=10.0,
                )
                if resp.status_code in (200, 201):
                    return True
                logger.warning(f"Failed to install app for team {team_id}: {resp.status_code} {resp.text}")
                return False
            except httpx.HTTPError as e:
                logger.error(f"HTTP error installing app for team: {e}")
                return False

    def deep_link_add_personal(self) -> Optional[str]:
        """Generate a deep link for adding the app in personal scope."""
        if not self.teams_app_id:
            return None
        return f"https://teams.microsoft.com/l/app/{self.teams_app_id}?installAppPackage=true"

    def deep_link_add_to_team(self, team_id: str) -> Optional[str]:
        """Generate a deep link for adding the app to a specific team."""
        if not self.teams_app_id:
            return None
        # Deep link to add to a team opens the add dialog pre-scoped to team
        return (
            f"https://teams.microsoft.com/l/app/{self.teams_app_id}?installAppPackage=true&teamId={team_id}"
        )

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
