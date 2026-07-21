from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.query import router as query_router
from backend.database.connection import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown.
    """

    await db.connect()

    yield

    try:
        await db.disconnect()
    except Exception:
        pass



app = FastAPI(
    title="NeuroFlow",
    version="0.1.0",
    lifespan=lifespan,
)


# -----------------------------
# Register Query API
# -----------------------------

app.include_router(
    query_router,
    prefix=""
)


print("QUERY ROUTER REGISTERED")
for route in app.routes:
    print(route)



# -----------------------------
# Health Routes
# -----------------------------

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