"""Slack API consumer for communicating with Slack services."""
import os
import logging
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class SlackAPIError(Exception):
    """Custom exception for Slack API errors."""
    pass


class SlackConsumer:
    """Slack API consumer for OAuth and messaging operations."""

    def __init__(self):
        """Initialize Slack consumer with configuration."""
        self.client_id = os.getenv("SLACK_CLIENT_ID")
        self.client_secret = os.getenv("SLACK_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SLACK_REDIRECT_URI")

        if not all([self.client_id, self.client_secret]):
            logger.warning("Slack credentials not configured")

    def get_oauth_url(self, state: str) -> str:
        """
        Generate Slack OAuth authorization URL.

        Args:
            state: CSRF protection state parameter

        Returns:
            OAuth authorization URL
        """
        scopes = [
            "channels:read",        # View basic channel info
            "channels:join",        # Join public channels when invited
            "chat:write",           # Send messages
            "groups:read",          # View private channels
            "im:read",              # View DM channel info
            "im:write",             # Open and send DMs
            "mpim:read",            # Read multi-party DMs
            "mpim:write",           # Write to multi-party DMs
            "users:read",           # Read user information
        ]

        user_scopes = [
            "channels:read",
            "groups:read",
        ]

        scope_string = ",".join(scopes)
        user_scope_string = ",".join(user_scopes)

        oauth_url = (
            f"https://slack.com/oauth/v2/authorize"
            f"?client_id={self.client_id}"
            f"&scope={scope_string}"
            f"&user_scope={user_scope_string}"
            f"&redirect_uri={self.redirect_uri}"
            f"&state={state}"
        )

        return oauth_url

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange OAuth code for access token.

        Args:
            code: OAuth authorization code

        Returns:
            Dict containing access token and user info

        Raises:
            SlackAPIError: If token exchange fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://slack.com/api/oauth.v2.access",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": self.redirect_uri,
                    }
                )

                data = response.json()

                if not data.get("ok"):
                    error_msg = data.get("error", "Unknown error")
                    logger.error(f"Slack OAuth error: {error_msg}")
                    raise SlackAPIError(f"OAuth failed: {error_msg}")

                return data

            except httpx.HTTPError as e:
                logger.error(f"HTTP error during Slack OAuth: {e}")
                raise SlackAPIError(f"HTTP error: {str(e)}")

    async def get_user_info(self, access_token: str, user_id: str) -> Dict[str, Any]:
        """
        Get Slack user information.

        Args:
            access_token: Slack access token
            user_id: Slack user ID

        Returns:
            User information dict

        Raises:
            SlackAPIError: If API call fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://slack.com/api/users.info",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={"user": user_id}
                )

                data = response.json()

                if not data.get("ok"):
                    error_msg = data.get("error", "Unknown error")
                    logger.error(f"Slack API error: {error_msg}")
                    raise SlackAPIError(f"Failed to get user info: {error_msg}")

                return data.get("user", {})

            except httpx.HTTPError as e:
                logger.error(f"HTTP error getting Slack user info: {e}")
                raise SlackAPIError(f"HTTP error: {str(e)}")

    async def open_dm_channel(self, access_token: str, user_id: str) -> str:
        """
        Open a DM channel with a user.

        Args:
            access_token: Slack access token
            user_id: Slack user ID

        Returns:
            Channel ID for the DM

        Raises:
            SlackAPIError: If API call fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://slack.com/api/conversations.open",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={"users": user_id}
                )

                data = response.json()

                if not data.get("ok"):
                    error_msg = data.get("error", "Unknown error")
                    logger.error(f"Slack API error opening DM: {error_msg}")
                    raise SlackAPIError(f"Failed to open DM: {error_msg}")

                channel = data.get("channel", {})
                return channel.get("id")

            except httpx.HTTPError as e:
                logger.error(f"HTTP error opening Slack DM: {e}")
                raise SlackAPIError(f"HTTP error: {str(e)}")

    async def send_message(
        self,
        access_token: str,
        channel_id: str,
        text: str,
        blocks: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Send a message to a Slack channel or DM.

        Args:
            access_token: Slack access token
            channel_id: Channel or DM ID
            text: Message text (fallback for notifications)
            blocks: Optional Block Kit blocks for rich formatting

        Returns:
            Message response data

        Raises:
            SlackAPIError: If message send fails
        """
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "channel": channel_id,
                    "text": text,
                }

                if blocks:
                    payload["blocks"] = blocks

                response = await client.post(
                    "https://slack.com/api/chat.postMessage",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json=payload
                )

                data = response.json()

                if not data.get("ok"):
                    error_msg = data.get("error", "Unknown error")
                    logger.error(f"Slack API error sending message: {error_msg}")
                    raise SlackAPIError(f"Failed to send message: {error_msg}")

                return data

            except httpx.HTTPError as e:
                logger.error(f"HTTP error sending Slack message: {e}")
                raise SlackAPIError(f"HTTP error: {str(e)}")

    async def get_bot_channels(self, access_token: str, bot_user_id: str) -> list[Dict[str, Any]]:
        """
        Get all channels/conversations the bot is a member of.

        Args:
            access_token: Slack access token
            bot_user_id: Bot user ID

        Returns:
            List of channel info dicts

        Raises:
            SlackAPIError: If API call fails
        """
        async with httpx.AsyncClient() as client:
            try:
                all_channels = []
                cursor = None

                while True:
                    params = {
                        "user": bot_user_id,
                        "types": "public_channel,private_channel",  # Only channels, not DMs
                        "exclude_archived": "true",
                        "limit": 100
                    }
                    if cursor:
                        params["cursor"] = cursor

                    response = await client.get(
                        "https://slack.com/api/users.conversations",
                        headers={"Authorization": f"Bearer {access_token}"},
                        params=params
                    )

                    data = response.json()

                    if not data.get("ok"):
                        error_msg = data.get("error", "Unknown error")
                        logger.error(f"Slack API error getting bot channels: {error_msg}")
                        raise SlackAPIError(f"Failed to get bot channels: {error_msg}")

                    channels = data.get("channels", [])
                    all_channels.extend(channels)

                    # Check if there are more pages
                    cursor = data.get("response_metadata", {}).get("next_cursor")
                    if not cursor:
                        break

                logger.info(f"Found {len(all_channels)} channels for bot {bot_user_id}")
                return all_channels

            except httpx.HTTPError as e:
                logger.error(f"HTTP error getting bot channels: {e}")
                raise SlackAPIError(f"HTTP error: {str(e)}")

    async def get_channel_info(self, access_token: str, channel_id: str) -> Dict[str, Any]:
        """
        Get information about a Slack channel.

        Args:
            access_token: Slack access token
            channel_id: Channel ID

        Returns:
            Channel information dict

        Raises:
            SlackAPIError: If API call fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://slack.com/api/conversations.info",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={"channel": channel_id}
                )

                data = response.json()

                if not data.get("ok"):
                    error_msg = data.get("error", "Unknown error")
                    logger.error(f"Slack API error getting channel info: {error_msg}")
                    raise SlackAPIError(f"Failed to get channel info: {error_msg}")

                return data.get("channel", {})

            except httpx.HTTPError as e:
                logger.error(f"HTTP error getting Slack channel info: {e}")
                raise SlackAPIError(f"HTTP error: {str(e)}")

    async def get_user_channels(self, access_token: str) -> list[Dict[str, Any]]:
        """
        Get all channels visible to the user (public + private).

        Args:
            access_token: Slack user access token

        Returns:
            List of channel info dicts
        """
        async with httpx.AsyncClient() as client:
            try:
                all_channels = []
                cursor = None

                while True:
                    params = {
                        "types": "public_channel,private_channel",
                        "exclude_archived": "true",
                        "limit": 200,
                    }
                    if cursor:
                        params["cursor"] = cursor

                    response = await client.get(
                        "https://slack.com/api/conversations.list",
                        headers={"Authorization": f"Bearer {access_token}"},
                        params=params,
                        timeout=10.0,
                    )

                    data = response.json()

                    if not data.get("ok"):
                        error_msg = data.get("error", "Unknown error")
                        logger.error(f"Slack API error getting user channels: {error_msg}")
                        raise SlackAPIError(f"Failed to get user channels: {error_msg}")

                    channels = data.get("channels", [])
                    all_channels.extend(channels)

                    cursor = data.get("response_metadata", {}).get("next_cursor")
                    if not cursor:
                        break

                logger.info(f"Found {len(all_channels)} channels visible to user")
                return all_channels

            except httpx.HTTPError as e:
                logger.error(f"HTTP error getting Slack user channels: {e}")
                raise SlackAPIError(f"HTTP error: {str(e)}")

    async def send_test_message(self, access_token: str, user_id: str, verification_url: Optional[str] = None) -> bool:
        """
        Send a test message to verify the connection.

        Args:
            access_token: Slack access token
            user_id: Slack user ID

        Returns:
            True if test message sent successfully

        Raises:
            SlackAPIError: If test message fails
        """
        try:
            # Open DM channel
            channel_id = await self.open_dm_channel(access_token, user_id)

            # Send test message
            test_blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🎉 Connection Successful!"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Your DRR (Domain Renewal Reminder) account is now connected to Slack! You'll receive important notifications about your domain and SSL certificate expirations directly here."
                    }
                },
            ]

            # Optionally add a verification button to confirm DM works
            if verification_url:
                test_blocks.append(
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "✅ Confirm in DRR"},
                                "url": verification_url
                            }
                        ]
                    }
                )

            # Footer divider and context
            test_blocks += [
                {
                    "type": "divider"
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "This is a test message from *Domain Renewal Reminder*"
                        }
                    ]
                }
            ]

            await self.send_message(
                access_token=access_token,
                channel_id=channel_id,
                text="🎉 Connection Successful! Your DRR account is now connected to Slack.",
                blocks=test_blocks
            )

            logger.info(f"Test message sent successfully to user {user_id}")
            return True

        except SlackAPIError as e:
            logger.error(f"Failed to send test message: {e}")
            raise


    async def uninstall_app(self, access_token: str) -> bool:
        """
        Attempt to uninstall the DRR Slack app from the workspace.

        Tries Slack's apps.uninstall endpoint using client credentials.
        Falls back to False if the workspace/app permissions disallow it.
        """
        async with httpx.AsyncClient() as client:
            try:
                # Slack docs: apps.uninstall expects client_id / client_secret and a token
                response = await client.post(
                    "https://slack.com/api/apps.uninstall",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "token": access_token,
                    },
                    timeout=10.0,
                )
                data = response.json()
                if not data.get("ok"):
                    logger.warning(f"Slack apps.uninstall failed: {data.get('error')}")
                    return False
                return True
            except httpx.HTTPError as e:
                logger.error(f"HTTP error uninstalling Slack app: {e}")
                return False

    async def revoke_token(self, access_token: str) -> bool:
        """
        Revoke the bot token to effectively disconnect the app for this workspace.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://slack.com/api/auth.revoke",
                    headers={"Authorization": f"Bearer {access_token}"},
                    data={"test": "false"},
                    timeout=10.0,
                )
                data = response.json()
                if not data.get("ok"):
                    logger.warning(f"Slack auth.revoke failed: {data.get('error')}")
                    return False
                return True
            except httpx.HTTPError as e:
                logger.error(f"HTTP error revoking Slack token: {e}")
                return False

# Global instance
slack_consumer = SlackConsumer()
