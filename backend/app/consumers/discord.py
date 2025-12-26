"""Discord Bot API consumer for communicating with Discord services."""
import os
import logging
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class DiscordAPIError(Exception):
    """Custom exception for Discord API errors."""
    pass


class DiscordConsumer:
    """Discord Bot API consumer for messaging operations."""

    def __init__(self):
        """Initialize Discord consumer with bot token and OAuth credentials."""
        self.bot_token = os.getenv("DISCORD_BOT_TOKEN")
        self.client_id = os.getenv("DISCORD_CLIENT_ID")
        self.client_secret = os.getenv("DISCORD_CLIENT_SECRET")
        self.redirect_uri = os.getenv("DISCORD_REDIRECT_URI")

        if not self.bot_token:
            logger.warning("Discord bot token not configured")
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            logger.warning("Discord OAuth credentials not fully configured")

        self.api_base = "https://discord.com/api/v10"

    def get_oauth_url(self, state: str) -> str:
        """Get Discord OAuth2 authorization URL."""
        scopes = "identify"
        return (
            f"https://discord.com/api/oauth2/authorize"
            f"?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code"
            f"&scope={scopes}"
            f"&state={state}"
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
                    "redirect_uri": self.redirect_uri
                }

                response = await client.post(
                    f"{self.api_base}/oauth2/token",
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10.0
                )

                if response.status_code != 200:
                    error_data = response.json() if response.text else {}
                    error_msg = error_data.get("error_description", "Token exchange failed")
                    logger.error(f"Discord OAuth token exchange failed: {error_msg}")
                    raise DiscordAPIError(f"Token exchange failed: {error_msg}")

                return response.json()

            except httpx.HTTPError as e:
                logger.error(f"HTTP error during Discord token exchange: {e}")
                raise DiscordAPIError(f"HTTP error: {str(e)}")

    async def get_current_user(self, access_token: str) -> Dict[str, Any]:
        """Get current user information using OAuth2 access token."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_base}/users/@me",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )

                if response.status_code != 200:
                    error_msg = f"Get user failed with status {response.status_code}"
                    logger.error(f"Discord API error getting user: {error_msg}")
                    raise DiscordAPIError(error_msg)

                return response.json()

            except httpx.HTTPError as e:
                logger.error(f"HTTP error getting Discord user: {e}")
                raise DiscordAPIError(f"HTTP error: {str(e)}")

    async def create_dm_channel(self, user_id: str) -> Dict[str, Any]:
        """Create a DM channel with a user."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_base}/users/@me/channels",
                    headers={
                        "Authorization": f"Bot {self.bot_token}",
                        "Content-Type": "application/json"
                    },
                    json={"recipient_id": user_id},
                    timeout=10.0
                )

                if response.status_code not in [200, 201]:
                    error_msg = f"Create DM failed with status {response.status_code}"
                    logger.error(f"Discord API error creating DM: {error_msg}")
                    raise DiscordAPIError(error_msg)

                return response.json()

            except httpx.HTTPError as e:
                logger.error(f"HTTP error creating Discord DM: {e}")
                raise DiscordAPIError(f"HTTP error: {str(e)}")

    async def send_message(self, channel_id: str, content: str, embeds: Optional[list] = None) -> Dict[str, Any]:
        """Send a message to a Discord channel or DM."""
        async with httpx.AsyncClient() as client:
            try:
                payload = {"content": content}
                if embeds:
                    payload["embeds"] = embeds

                response = await client.post(
                    f"{self.api_base}/channels/{channel_id}/messages",
                    headers={
                        "Authorization": f"Bot {self.bot_token}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=10.0
                )

                if response.status_code not in [200, 201]:
                    error_data = response.json() if response.text else {}
                    error_msg = error_data.get("message", f"Send message failed with status {response.status_code}")
                    logger.error(f"Discord API error sending message: {error_msg}")
                    raise DiscordAPIError(f"Send message failed: {error_msg}")

                return response.json()

            except httpx.HTTPError as e:
                logger.error(f"HTTP error sending Discord message: {e}")
                raise DiscordAPIError(f"HTTP error: {str(e)}")

    async def send_test_message(self, channel_id: str, username: Optional[str] = None, verification_url: Optional[str] = None) -> Dict[str, Any]:
        """Send a test message to verify the integration."""
        greeting = f"Hi {username}! " if username else "Hi! "
        content = (
            f"{greeting}🎉\n\n"
            f"**DRR Test Connection**\n\n"
            f"Your Discord integration is working correctly!\n\n"
        )

        if verification_url:
            content += f"Click the link below to confirm and activate your connection:\n{verification_url}\n\n"

        content += "Domain Renewal Reminder"

        return await self.send_message(channel_id, content)



# Global instance
discord_consumer = DiscordConsumer()