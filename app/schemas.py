"""Pydantic schemas for requests and responses."""

import datetime as dt

from pydantic import BaseModel, Field, field_validator

from . import services


def validate_target_url(value: str) -> str:
    if not services.is_allowed_url(value):
        raise ValueError(
            "URL must use http/https scheme, include a host "
            "and contain no whitespace or control characters"
        )
    return value


class LinkCreate(BaseModel):
    """Request body for creating a short link."""

    url: str = Field(min_length=1, max_length=2048, description="Target URL to shorten")

    @field_validator("url")
    @classmethod
    def check_url(cls, value: str) -> str:
        return validate_target_url(value)


class LinkOut(BaseModel):
    """Response with the created short link."""

    code: str
    url: str
    short_url: str
    clicks: int

    model_config = {"populate_by_name": True, "from_attributes": True}


class LinkStats(BaseModel):
    """Usage statistics for a single short link."""

    code: str
    url: str
    clicks: int
    created_at: dt.datetime

    model_config = {"populate_by_name": True, "from_attributes": True}
