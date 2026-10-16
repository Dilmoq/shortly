"""ORM models."""

import datetime as dt

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Link(Base):
    """A shortened link and its usage statistics."""

    __tablename__ = "links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    # The target URL the short code redirects to.
    target_url: Mapped[str] = mapped_column(String(2048))
    # Number of times the redirect endpoint was used.
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Link code={self.code!r} target={self.target_url!r} clicks={self.clicks}>"
