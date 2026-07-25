import asyncio
from contextlib import asynccontextmanager, suppress
from backend.api.evaluations import router as evaluation_router
from fastapi import FastAPI

from backend.database.connection import db

from backend.api.query import router as query_router
from backend.api.rating import router as rating_router
from backend.api.pipeline import router as pipeline_router
from backend.queue.evaluation_queue import (
    process_evaluation_queue,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown.
    """

    # ---------------------------------
    # Connect Database
    # ---------------------------------

    await db.connect()

    print("Connected to PostgreSQL")

    # ---------------------------------
    # Start Evaluation Worker
    # ---------------------------------

    evaluation_worker = asyncio.create_task(
        process_evaluation_queue()
    )

    print("Evaluation worker started.")

    yield

    # ---------------------------------
    # Shutdown Worker
    # ---------------------------------

    evaluation_worker.cancel()

    with suppress(asyncio.CancelledError):
        await evaluation_worker

    # ---------------------------------
    # Disconnect Database
    # ---------------------------------

    await db.disconnect()

    print("Disconnected from PostgreSQL")


app = FastAPI(
    title="NeuroFlow",
    version="0.1.0",
    lifespan=lifespan,
)

# ---------------------------------
# Register Routers
# ---------------------------------

app.include_router(
    query_router,
)

app.include_router(
    rating_router,
)

app.include_router(
    evaluation_router,
) 
app.include_router(pipeline_router)

print("QUERY ROUTER REGISTERED")

for route in app.routes:
    print(route)


# ---------------------------------
# Root
# ---------------------------------

@app.get("/")
async def root():

    return {
        "message": "NeuroFlow API running"
    }


# ---------------------------------
# Health
# ---------------------------------

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


# ---------------------------------
# Metrics
# ---------------------------------

@app.get("/metrics")
async def metrics():

    return "neuroflow_requests_total 0"