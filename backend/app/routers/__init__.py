"""Router package exports.

Explicitly import router submodules so that consumers using
`from app.routers import <module>` succeed reliably in all
environments (including CI).
"""

from . import health  # noqa: F401
from . import auth  # noqa: F401
from . import users  # noqa: F401
from . import slack  # noqa: F401
from . import telegram  # noqa: F401
from . import discord  # noqa: F401
from . import teams  # noqa: F401
from . import cases  # noqa: F401

__all__ = [
    "health",
    "auth",
    "users",
    "slack",
    "telegram",
    "discord",
    "teams",
    "cases",
]
