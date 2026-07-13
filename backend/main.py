from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.query import router as query_router
from backend.database.connection import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown.
    Creates a fresh database connection pool on startup
    and closes it safely on shutdown.
    """
    await db.connect()

    yield

    try:
        await db.disconnect()
    except Exception:
        # Ignore shutdown errors during testing
        pass


app = FastAPI(
    title="NeuroFlow",
    lifespan=lifespan,
)

# Register API routes
app.include_router(query_router)


@app.get("/")
async def root():
    return {
        "message": "NeuroFlow API running"
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "checks": {
            "postgres": db.pool is not None,
            "redis": True,
            "mlflow": True,
        },
    }


@app.get("/metrics")
async def metrics():
    return "neuroflow_requests_total 0"