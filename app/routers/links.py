"""API endpoints under the /api prefix."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import config, schemas
from ..database import get_db
from ..models import Link
from ..services import generate_short_code

router = APIRouter()

_CODE_MAX_ATTEMPTS = 10


def build_short_url(request: Request, code: str) -> str:
    """Build an absolute short URL for the given code."""
    base = config.BASE_URL.rstrip("/")
    return f"{base}/{code}"


@router.post(
    "/links",
    response_model=schemas.LinkOut,
    status_code=status.HTTP_201_CREATED,
)
def create_short_link(
    payload: schemas.LinkCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> schemas.LinkOut:
    """Shorten a URL. Returns a unique generated code."""
    link = Link(code="", target_url=payload.url)  # code assigned below
    for _ in range(_CODE_MAX_ATTEMPTS):
        code = generate_short_code()
        if db.scalar(select(Link).where(Link.code == code)) is not None:
            continue
        link.code = code
        db.add(link)
        try:
            db.commit()
        except IntegrityError:  # race with another worker
            db.rollback()
            continue
        break
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate a unique code, please retry",
        )

    return schemas.LinkOut(
        code=link.code,
        url=link.target_url,
        short_url=build_short_url(request, link.code),
        clicks=link.clicks,
    )


@router.get("/links/{code}/stats", response_model=schemas.LinkStats)
def get_link_stats(code: str, db: Session = Depends(get_db)) -> schemas.LinkStats:
    """Return click statistics for a short link."""
    link = db.scalar(select(Link).where(Link.code == code))
    if link is None:
        raise HTTPException(status_code=404, detail="Short link not found")
    return schemas.LinkStats(
        code=link.code,
        url=link.target_url,
        clicks=link.clicks,
        created_at=link.created_at,
    )
