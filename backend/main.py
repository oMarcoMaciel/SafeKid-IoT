from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.database import engine, Base
from .core.mqtt_client import mqtt_client
from .modules.cards.router import router as cards_router
from .modules.metrics.router import router as metrics_router
from .modules.tracking.router import router as tracking_router
from .modules.scanners.router import router as scanners_router

# Import models to ensure they are registered with Base for migrations/creation
from .modules.cards.models import Card, AccessLog
from .modules.tracking.models import TrackingLog
from .modules.scanners.models import Scanner

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start MQTT client
    mqtt_client.start()
    yield
    # Shutdown: Stop MQTT client
    mqtt_client.stop()

app = FastAPI(title="SafeKid API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cards_router)
app.include_router(metrics_router)
app.include_router(tracking_router)
app.include_router(scanners_router)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
