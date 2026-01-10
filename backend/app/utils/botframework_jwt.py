"""Bot Framework JWT validation utilities (dev-friendly).

Validates Teams/Bot Framework auth tokens using OpenID metadata and jose.
"""
import time
import logging
from typing import Optional, Dict, Any
import httpx
from jose import jwt

logger = logging.getLogger(__name__)

OPENID_CONFIG_MAP = {
    "public": "https://login.botframework.com/v1/.well-known/openidconfiguration",
    "usgov": "https://login.botframework.us/v1/.well-known/openidconfiguration",
    "china": "https://login.botframework.azure.cn/v1/.well-known/openidconfiguration",
}
ISSUER_MAP = {
    "public": "https://api.botframework.com",
    "usgov": "https://api.botframework.us",
    "china": "https://api.botframework.azure.cn",
}
_CACHE: Dict[str, Any] = {"jwks": None, "jwks_fetched_at": 0, "jwks_uri": None, "openid_url": None}


async def _get_openid_cfg(openid_config_url: str) -> Optional[Dict[str, Any]]:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(openid_config_url, timeout=10.0)
            if resp.status_code != 200:
                logger.error(f"Failed to fetch OpenID config: {resp.status_code} {resp.text}")
                return None
            return resp.json()
    except Exception as e:
        logger.error(f"Error fetching OpenID config: {e}")
        return None


async def _get_jwks(openid_config_url: str) -> Optional[Dict[str, Any]]:
    now = time.time()
    if (
        _CACHE.get("jwks")
        and _CACHE.get("openid_url") == openid_config_url
        and now - _CACHE.get("jwks_fetched_at", 0) < 3600
    ):
        return _CACHE["jwks"]
    cfg = await _get_openid_cfg(openid_config_url)
    if not cfg:
        return None
    jwks_uri = cfg.get("jwks_uri")
    if not jwks_uri:
        logger.error("OpenID config missing jwks_uri")
        return None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(jwks_uri, timeout=10.0)
            if resp.status_code != 200:
                logger.error(f"Failed to fetch JWKS: {resp.status_code} {resp.text}")
                return None
            _CACHE["jwks"] = resp.json()
            _CACHE["jwks_uri"] = jwks_uri
            _CACHE["jwks_fetched_at"] = now
            _CACHE["openid_url"] = openid_config_url
            return _CACHE["jwks"]
    except Exception as e:
        logger.error(f"Error fetching JWKS: {e}")
        return None


async def verify_bot_jwt(
    auth_header: str,
    audience: str,
    expected_service_url: Optional[str] = None,
    channel_service: str = "public",
) -> Dict[str, Any]:
    """Verify Bot Framework JWT. Returns claims if valid; raises ValueError otherwise."""
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise ValueError("Missing or invalid Authorization header")
    token = auth_header.split(" ", 1)[1].strip()

    openid_url = OPENID_CONFIG_MAP.get(channel_service, OPENID_CONFIG_MAP["public"])
    issuer = ISSUER_MAP.get(channel_service, ISSUER_MAP["public"])
    jwks = await _get_jwks(openid_url)
    if not jwks:
        raise ValueError("Unable to fetch JWKS for validation")

    try:
        claims = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=audience,
            issuer=issuer,
            options={"verify_exp": True},
        )
    except Exception as e:
        logger.error(f"JWT validation failed: {e}")
        raise ValueError("Invalid token")

    if expected_service_url:
        svc = claims.get("serviceurl") or claims.get("serviceUrl")
        if svc and svc != expected_service_url:
            raise ValueError("serviceUrl mismatch")

    return claims
