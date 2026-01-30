"""Service for retrieving WHOIS and SSL certificate data for a domain."""

# from __future__ import annotations

from datetime import datetime
# import shutil
import socket
import ssl
from typing import Any, Dict, Optional

# import whois


class SslService:
    """Utility service for gathering information about a domain name."""

    def __init__(self, domain: str):
        self.domain = self._normalize_domain(domain)

    @staticmethod
    def _normalize_domain(domain: str) -> str:
        """Normalize the domain by removing a leading ``www.`` if present."""
        domain = domain.strip().lower()
        if domain.startswith("www."):
            return domain[4:]
        return domain

    def get_cert(self, port: int = 443) -> Dict[str, Any]:
        """Retrieve SSL certificate information for the domain.

        Parameters
        ----------
        port: int
            The port to use when connecting to the domain. Defaults to ``443``.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing certificate details such as issuer and
            expiration date.
        """

        context = ssl.create_default_context()
        with socket.create_connection((self.domain, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                cert = ssock.getpeercert()
                print(cert)

        issuer = {k: v for item in cert.get("issuer", []) for k, v in item}
        subject = {k: v for item in cert.get("subject", []) for k, v in item}

        not_before_str: Optional[str] = cert.get("notBefore")
        not_after_str: Optional[str] = cert.get("notAfter")
        not_before = (
            datetime.strptime(not_before_str, "%b %d %H:%M:%S %Y %Z")
            if not_before_str
            else None
        )
        not_after = (
            datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z")
            if not_after_str
            else None
        )

        return {
            "subject": subject,
            "issuer": issuer,
            "not_before": not_before,
            "not_after": not_after,
            "serial_number": cert.get("serialNumber"),
            "version": cert.get("version"),
        }


if __name__ == "__main__":
    # import ssl
    # ssl._create_default_https_context = ssl._create_unverified_context  # Temporary workaround
    ssl_service = SslService("nova.rs")
    print(ssl_service.get_cert())

