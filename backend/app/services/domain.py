"""Service for retrieving WHOIS data for a domain."""
from __future__ import annotations

import whois
import shutil
from typing import Any, Dict


class DomainService:
    """Utility service for gathering information about a domain name."""

    RESTRICTED = "restricted"

    def __init__(self, domain: str):
        self.domain = self._normalize_domain(domain)

    @staticmethod
    def _normalize_domain(domain: str) -> str:
        """Normalize the domain by removing a leading ``www.`` if present."""
        domain = domain.strip().lower()
        if domain.startswith("www."):
            return domain[4:]
        return domain

    def get_whois(self) -> Dict[str, Any]:
        """Return WHOIS information for the domain.

        The project depends on the ``python-whois`` package which exposes a
        :func:`whois` function.  Some environments may instead provide the
        ``whois`` package whose API uses :func:`query`.  To remain compatible
        (and to avoid ``AttributeError`` when the expected function is missing)
        this method tries both interfaces.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the most common WHOIS fields.
        """

        # Determine which lookup function is available.  ``python-whois``
        # exposes ``whois`` whereas the ``whois`` package exposes ``query``.
        if hasattr(whois, "whois"):
            lookup = whois.whois
        elif hasattr(whois, "query"):
            # The ``whois`` package shells out to a ``whois`` executable which
            # is not always present (e.g. on Windows by default).  Detect this
            # early so we can raise a helpful error message instead of letting
            # ``subprocess`` raise ``FileNotFoundError`` deep in the call stack.
            if shutil.which("whois") is None:
                raise RuntimeError(
                    "The installed 'whois' package requires the system 'whois' "
                    "command, which could not be found. Install the 'python-whois' "
                    "package or add the command to your PATH."
                )
            lookup = whois.query
        else:  # pragma: no cover - defensive programming
            raise RuntimeError("A compatible whois library is not installed.")

        try:
            data = lookup(self.domain)
        except FileNotFoundError as exc:  # pragma: no cover - missing whois CLI
            raise RuntimeError(
                "The system 'whois' command could not be executed. Install it or "
                "install the 'python-whois' package."
            ) from exc
        except Exception as exc:  # pragma: no cover - network errors etc.
            raise RuntimeError("WHOIS lookup failed") from exc

        domain_name = getattr(data, "domain_name", getattr(data, "name", None))

        # ``domain_name`` may be a list; normalise and ensure it matches the
        # requested domain.  If it does not, the lookup likely returned data for
        # a different domain and an empty result is safer than propagating
        # incorrect information.
        if isinstance(domain_name, list):
            domain_names = [self._normalize_domain(d) for d in domain_name if isinstance(d, str)]
        elif isinstance(domain_name, str):
            domain_names = [self._normalize_domain(domain_name)]
        else:
            domain_names = []

        if self.domain not in domain_names:
            return {}

        creation_date = getattr(data, "creation_date", self.RESTRICTED)
        if isinstance(creation_date, list):
            creation_date = creation_date[0] if creation_date else self.RESTRICTED

        updated_date = getattr(data, "updated_date", getattr(data, "last_updated", None))
        if isinstance(updated_date, list):
            updated_date = updated_date[-1] if updated_date else None

        expiration_date = getattr(data, "expiration_date", self.RESTRICTED)
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0] if expiration_date else self.RESTRICTED

        return {
            "domain_name": domain_name,
            "registrar": getattr(data, "registrar", self.RESTRICTED),
            "creation_date": creation_date,
            "updated_date": updated_date,
            "expiration_date": expiration_date,
            "name_servers": getattr(data, "name_servers", None),
        }


if __name__ == "__main__":
    domain_service = DomainService("leasingmarkt.de")
    print(domain_service.get_whois())


