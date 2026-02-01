"""Domains router for domain and SSL monitoring."""
import logging
from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.database.database import get_db
from app.models.domain import Domain, DomainType
from app.models.users import User
from app.schemas.domain import DomainResponse
from app.utils.security import get_current_user, get_current_superuser
from app.services.domain import DomainService
from app.services.ssl_service import SslService
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/domains", tags=["domains"])


class AddDomainRequest(BaseModel):
    """Schema for adding a domain."""
    name: str = Field(..., max_length=256, description="Domain name")


class AddSSLRequest(BaseModel):
    """Schema for adding an SSL certificate."""
    name: str = Field(..., max_length=256, description="Domain name or subdomain")


@router.post("/add-domain", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
async def add_domain(
    request: AddDomainRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Add a new domain to monitor (superuser only).

    Retrieves WHOIS information for the domain and stores it in the database.
    """
    try:
        # Normalize domain name
        domain_name = request.name.strip().lower()
        if domain_name.startswith("www."):
            domain_name = domain_name[4:]

        # Check if domain already exists for this company
        result = await db.execute(
            select(Domain).where(
                and_(
                    Domain.company_id == current_user.company_id,
                    Domain.name == domain_name,
                    Domain.type == DomainType.DOMAIN,
                    Domain.deleted_at.is_(None)
                )
            )
        )
        existing_domain = result.scalar_one_or_none()

        if existing_domain:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Domain '{domain_name}' already exists in your monitoring list"
            )

        # Get WHOIS information
        try:
            domain_service = DomainService(domain_name)
            whois_data = domain_service.get_whois()

            if not whois_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Could not retrieve WHOIS data for domain '{domain_name}'. Please check the domain name."
                )

            # Extract expiration date
            expiration_date = whois_data.get("expiration_date")
            if expiration_date == "restricted" or not expiration_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Expiration date for domain '{domain_name}' is restricted or unavailable"
                )

            # Convert to date if datetime
            if hasattr(expiration_date, 'date'):
                expiration_date = expiration_date.date()

            registrar = whois_data.get("registrar", "Unknown")
            if registrar == "restricted":
                registrar = "Unknown"

        except Exception as e:
            logger.error(f"Error fetching WHOIS data for {domain_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve domain information: {str(e)}"
            )

        # Create domain record
        new_domain = Domain(
            company_id=current_user.company_id,
            name=domain_name,
            type=DomainType.DOMAIN,
            renew_date=expiration_date,
            issuer=registrar[:128],  # Truncate if needed
            issuer_link=None
        )

        db.add(new_domain)
        await db.commit()
        await db.refresh(new_domain)

        logger.info(f"Domain {domain_name} added by user {current_user.email}")
        logger.info(f"Domain object: id={new_domain.id}, type={new_domain.type}, type_value={new_domain.type.value if hasattr(new_domain.type, 'value') else new_domain.type}")
        return new_domain

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding domain: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add domain"
        )


@router.post("/add-ssl", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
async def add_ssl(
    request: AddSSLRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Add a new SSL certificate to monitor (superuser only).

    Retrieves SSL certificate information for the domain/IP and stores it in the database.
    """
    try:
        # Normalize name
        name = request.name.strip().lower()
        if name.startswith("www."):
            name = name[4:]

        # Check if SSL already exists for this company
        result = await db.execute(
            select(Domain).where(
                and_(
                    Domain.company_id == current_user.company_id,
                    Domain.name == name,
                    Domain.type == DomainType.SSL,
                    Domain.deleted_at.is_(None)
                )
            )
        )
        existing_ssl = result.scalar_one_or_none()

        if existing_ssl:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"SSL certificate for '{name}' already exists in your monitoring list"
            )

        # Get SSL certificate information
        try:
            ssl_service = SslService(name)
            cert_data = ssl_service.get_cert()

            if not cert_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Could not retrieve SSL certificate for '{name}'"
                )

            # Extract certificate data
            not_after = cert_data.get("not_after")
            not_before = cert_data.get("not_before")
            issuer_data = cert_data.get("issuer", {})

            # Get issuer name
            issuer_name = (
                issuer_data.get("organizationName") or
                issuer_data.get("commonName") or
                "Unknown CA"
            )

            if not not_after:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Could not determine expiration date for SSL certificate on '{name}'"
                )

            # Convert to date
            expiration_date = not_after.date() if hasattr(not_after, 'date') else not_after

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching SSL certificate for {name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve SSL certificate: {str(e)}"
            )

        # Create SSL record
        new_ssl = Domain(
            company_id=current_user.company_id,
            name=name,
            type=DomainType.SSL,
            renew_date=expiration_date,
            issuer=issuer_name[:128],
            issuer_link=None,
            not_before=not_before
        )

        db.add(new_ssl)
        await db.commit()
        await db.refresh(new_ssl)

        logger.info(f"SSL certificate for {name} added by user {current_user.email}")
        logger.info(f"SSL object: id={new_ssl.id}, type={new_ssl.type}, type_value={new_ssl.type.value if hasattr(new_ssl.type, 'value') else new_ssl.type}")
        return new_ssl

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding SSL certificate: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add SSL certificate"
        )


@router.get("/", response_model=List[DomainResponse])
async def list_domains(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all domains and SSL certificates for the current user's company.
    """
    try:
        logger.info(f"Fetching domains for company: {current_user.company_id}")
        result = await db.execute(
            select(Domain)
            .where(
                and_(
                    Domain.company_id == current_user.company_id,
                    Domain.deleted_at.is_(None)
                )
            )
            .order_by(Domain.created_at.desc())
        )
        domains = result.scalars().all()
        logger.info(f"Found {len(domains)} domains for company {current_user.company_id}")

        # Log domain details for debugging
        for domain in domains:
            logger.info(f"Domain: id={domain.id}, name={domain.name}, type={domain.type}, type_value={domain.type.value if hasattr(domain.type, 'value') else domain.type}")

        return domains
    except Exception as e:
        logger.error(f"Error listing domains: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve domains"
        )


@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_domain(
    domain_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Delete a domain or SSL certificate (soft delete).
    """
    try:
        result = await db.execute(
            select(Domain).where(
                and_(
                    Domain.id == domain_id,
                    Domain.company_id == current_user.company_id,
                    Domain.deleted_at.is_(None)
                )
            )
        )
        domain = result.scalar_one_or_none()

        if not domain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain not found"
            )

        # Soft delete
        from datetime import datetime
        domain.deleted_at = datetime.utcnow()
        await db.commit()

        logger.info(f"Domain {domain.name} deleted by user {current_user.email}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting domain: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete domain"
        )
