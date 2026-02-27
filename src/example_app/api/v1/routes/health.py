"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/healthz", summary="Health check")
async def health_check_root() -> str:
    """Health check endpoint at root.

    Returns:
        Health status
    """
    return "ok"


@router.get("/readyz", summary="Readiness probe")
async def readiness_check() -> str:
    """Readiness probe endpoint.

    Returns:
        Health status
    """
    return "ok"


@router.get("/livez", summary="Liveness probe")
async def liveness_check() -> str:
    """Liveness probe endpoint.

    Returns:
        Health status
    """
    return "ok"
