"""Redirect endpoint on the root path (/api prefix is not merged here)."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Link
from ..services import is_allowed_url

router = APIRouter()


@router.get("/{code}", include_in_schema=False)
def redirect_to_target(code: str, db: Session = Depends(get_db)) -> RedirectResponse:
    """Increment the click counter and redirect to the target URL."""
    # Cheap guard so junk paths fall through to 404 without touching the DB.
    if len(code) > 32 or not code.isalnum():
        raise HTTPException(status_code=404, detail="Short link not found")
    link = db.scalar(select(Link).where(Link.code == code))
    if link is None or not is_allowed_url(link.target_url):
        raise HTTPException(status_code=404, detail="Short link not found")
    link.clicks += 1
    db.commit()
    return RedirectResponse(url=link.target_url, status_code=status.HTTP_302_FOUND)
