"""WebSocket server entry and lifecycle.

FastAPI WebSocket server with:
- Connection management and room broadcasting (vehicle/fleet)
- JWT/API-key authentication
- Heartbeat pings and reconnection handling
- Message queuing per client when paused/offline
- Simple token-bucket rate limiting per connection
"""

from __future__ import annotations

import asyncio
import json
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Optional, Set
from urllib.parse import urlparse, parse_qs
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..api.middleware.auth import authenticate_request

router = APIRouter()


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


hub = WsHub()


@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
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