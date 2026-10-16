"""Application entry point: FastAPI app factory.

Run locally:
    uvicorn app.main:app --reload
"""

from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .database import init_db
from .routers import links, redirect


def create_app() -> FastAPI:
    """Build the FastAPI application."""
    app = FastAPI(
        title="shortly",
        description="A URL shortener service: create short links, "
        "redirect users and track click statistics.",
        version=__version__,
        lifespan=_lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    # Service meta routes must be registered BEFORE the /{code} catch-all.
    @app.get("/health", tags=["meta"])
    def health() -> dict[str, str]:
        """Liveness probe."""
        return {"status": "ok"}

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> dict[str, str]:
        return {"status": "no favicon"}

    app.include_router(links.router, prefix="/api")
    # Must be registered last: it has a /{code} catch-all.
    app.include_router(redirect.router)

    return app


async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


# Module-level app instance used by `uvicorn app.main:app`.
app = create_app()
