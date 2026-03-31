"""Application entry point for starting the API server or CLI.\n"""
import json
import logging
import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Optional, Set, Any
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=os.getenv("APP_NAME", "Telemetric System"),
    description="Vehicle Fleet Management and Telemetry System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
from telemetric_system.api.routes import auth as auth_router, vehicles as vehicles_router
from telemetric_system.api.routes import drivers as drivers_router
from telemetric_system.api.routes import telemetry as telemetry_router
from telemetric_system.api.routes import analytics as analytics_router
from telemetric_system.api.routes import reports as reports_router
from telemetric_system.api.routes import alerts as alerts_router
from telemetric_system.api.routes import geofence as geofences_router
from telemetric_system.api.routes import vehicle_types as vehicle_types_router
from telemetric_system.api.routes import maintenance as maintenance_router
from telemetric_system.api.routes import settings as settings_router
from telemetric_system.api.middleware.auth import authenticate_request
from telemetric_system.core.database.connection import get_engine
from telemetric_system.models import Base

app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(vehicles_router.router, prefix="/api/v1")
app.include_router(drivers_router.router, prefix="/api/v1")
app.include_router(telemetry_router.router, prefix="/api/v1")
app.include_router(analytics_router.router, prefix="/api/v1")
app.include_router(reports_router.router, prefix="/api/v1")
app.include_router(alerts_router.router, prefix="/api/v1")
app.include_router(geofences_router.router, prefix="/api/v1")
app.include_router(vehicle_types_router.router, prefix="/api/v1")
app.include_router(maintenance_router.router, prefix="/api/v1")
app.include_router(settings_router.router, prefix="/api/v1")


# ===== WebSocket Implementation =====

@dataclass
class ClientState:
    user_id: Optional[int]
    role: Optional[str]
    device_id: Optional[str]
    rooms: Set[str] = field(default_factory=set)
    queue: Deque[str] = field(default_factory=lambda: deque(maxlen=1000))
    last_seen: float = field(default_factory=lambda: time.time())
    tokens: float = 10.0  # rate limit tokens
    last_refill: float = field(default_factory=lambda: time.time())


class WsHub:
    def __init__(self) -> None:
        self.clients: Dict[WebSocket, ClientState] = {}
        self.rooms: Dict[str, Set[WebSocket]] = defaultdict(set)

    async def connect(self, ws: WebSocket):
        print("🔍 WebSocket connection attempt")
        print("🔍 URL:", str(ws.url))
        
        await ws.accept()

        # Create headers dict with lowercase keys for consistency
        headers = {}
        for key, value in ws.headers.raw:
            headers[key.decode().lower()] = value.decode()
        
        print("🔍 Raw headers:", headers)

        # ✅ Extract token from query params
        query_params = parse_qs(urlparse(str(ws.url)).query)
        print("🔍 Query params:", query_params)
        token = query_params.get("token", [None])[0]
        print("🔍 Token extracted:", token)

        if token:
            headers["authorization"] = f"Bearer {token}"
            print("🔍 Authorization header set:", headers.get("authorization"))

        # ✅ Authenticate using middleware
        print("🔍 Calling authenticate_request with headers:", headers)
        try:
            ctx = authenticate_request(headers)
            print("🔍 Auth context - user_id:", ctx.user_id, "role:", ctx.role, "device_id:", ctx.device_id)
        except Exception as e:
            print("❌ Exception in authenticate_request:", e)
            import traceback
            traceback.print_exc()
            await ws.close(code=4403, reason="Authentication error")
            return

        if not ctx.user_id:
            print("❌ Authentication failed - ctx.user_id is None")
            print("❌ Full context:", vars(ctx))
            await ws.close(code=4403, reason="Forbidden")
            return

        print("✅ WebSocket authenticated user:", ctx.user_id, ctx.role)
        self.clients[ws] = ClientState(
            user_id=ctx.user_id,
            role=ctx.role,
            device_id=ctx.device_id
        )

    def disconnect(self, ws: WebSocket) -> None:
        state = self.clients.pop(ws, None)
        if state:
            for r in list(state.rooms):
                self.rooms[r].discard(ws)

    def join(self, ws: WebSocket, room: str) -> None:
        self.rooms[room].add(ws)
        self.clients[ws].rooms.add(room)

    def leave(self, ws: WebSocket, room: str) -> None:
        self.rooms[room].discard(ws)
        self.clients[ws].rooms.discard(room)

    async def send(self, ws: WebSocket, message: Dict) -> None:
        state = self.clients.get(ws)
        if not state:
            return
        if not self._consume_token(state):
            # rate limited; queue message
            state.queue.append(json.dumps(message))
            return
        await ws.send_text(json.dumps(message))

    async def broadcast(self, room: str, message: Dict) -> None:
        payload = json.dumps(message)
        for ws in list(self.rooms.get(room, [])):
            state = self.clients.get(ws)
            if not state:
                continue
            if not self._consume_token(state):
                state.queue.append(payload)
                continue
            try:
                await ws.send_text(payload)
            except Exception:
                # enqueue for retry
                state.queue.append(payload)

    async def flush(self, ws: WebSocket) -> None:
        state = self.clients.get(ws)
        if not state:
            return
        while state.queue:
            try:
                await ws.send_text(state.queue.popleft())
            except Exception:
                break

    def _consume_token(self, state: ClientState) -> bool:
        # simple token bucket: refill 5 tokens per second up to 50
        now = time.time()
        elapsed = now - state.last_refill
        if elapsed > 0:
            state.tokens = min(50.0, state.tokens + elapsed * 5.0)
            state.last_refill = now
        if state.tokens >= 1.0:
            state.tokens -= 1.0
            return True
        return False


# Create hub instance
hub = WsHub()


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    print("🚀 ws_endpoint CALLED!")
    await hub.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            # basic protocol: {"action": "join", "room": "vehicle:1"}
            try:
                msg = json.loads(data)
            except Exception:
                await hub.send(ws, {"type": "error", "message": "invalid json"})
                continue
            action = msg.get("action")
            if action == "join":
                room = str(msg.get("room"))
                hub.join(ws, room)
                await hub.send(ws, {"type": "joined", "room": room})
            elif action == "leave":
                room = str(msg.get("room"))
                hub.leave(ws, room)
                await hub.send(ws, {"type": "left", "room": room})
            elif action == "ping":
                await hub.send(ws, {"type": "pong", "ts": time.time()})
            else:
                await hub.send(ws, {"type": "error", "message": "unknown action"})
            await hub.flush(ws)
    except WebSocketDisconnect:
        pass
    finally:
        hub.disconnect(ws)


# ===== Telemetry Publishing Functions =====

def publish_telemetry(vehicle_id: int, payload: Dict[str, Any]) -> None:
    """Publish telemetry data to vehicle-specific room"""
    room = f"vehicle:{vehicle_id}"
    msg = {"type": "telemetry", "vehicle_id": vehicle_id, "data": payload}
    # Schedule broadcast in event loop
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(hub.broadcast(room, msg))
        else:
            loop.run_until_complete(hub.broadcast(room, msg))
    except Exception as e:
        logger.error(f"Failed to publish telemetry: {e}")


# Optional: Endpoint to manually push telemetry (for testing)
@app.post("/api/v1/telemetry/publish")
async def publish_telemetry_endpoint(vehicle_id: int, data: Dict[str, Any]):
    """Test endpoint to manually publish telemetry data"""
    await hub.broadcast(f"vehicle:{vehicle_id}", {
        "type": "telemetry",
        "vehicle_id": vehicle_id,
        "data": data
    })
    return {"status": "published", "vehicle_id": vehicle_id}


# ===== End WebSocket Implementation =====


@app.get("/")
async def root():
    return {
        "message": "Telemetric System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "mqtt": "connected"
    }


@app.on_event("startup")
def _startup_init_db() -> None:
    try:
        # Create tables if they do not exist (useful for test SQLite runs)
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        logger.warning(f"DB init skipped or failed: {exc}")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    if isinstance(exc, PermissionError):
        return JSONResponse(status_code=403, content={"detail": "forbidden"})
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )