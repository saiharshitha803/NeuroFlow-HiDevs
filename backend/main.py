from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting NeuroFlow...")
    yield
    print("Stopping NeuroFlow...")


app = FastAPI(
    title="NeuroFlow",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "NeuroFlow API running"}


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "checks": {
            "postgres": True,
            "redis": True,
            "mlflow": True
        }
    }


@app.get("/metrics")
async def metrics():
    return "neuroflow_requests_total 0"