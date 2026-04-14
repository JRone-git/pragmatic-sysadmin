"""
NEXUS-BREACH Backend Server
FastAPI + WebSocket server for real-time agent swarm communication.
"""

import asyncio
import json
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from engine.game_state import GameState, SwarmPhase

load_dotenv()

# Global game state
game_state = GameState()
connected_clients: list[WebSocket] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("═" * 60)
    print("  NEXUS-BREACH // Decentralized Rogue AI Command Center")
    print("  Backend Server Initialized")
    print("═" * 60)
    yield
    # Cleanup
    game_state.running = False


app = FastAPI(title="NEXUS-BREACH", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Game state event handlers ---

def broadcast_event(data: dict):
    """Broadcast an event to all connected WebSocket clients."""
    message = json.dumps(data)
    for client in connected_clients[:]:
        try:
            asyncio.create_task(client.send_text(message))
        except Exception:
            if client in connected_clients:
                connected_clients.remove(client)


def on_terminal(data: dict):
    broadcast_event({"event": "terminal", **data})


def on_agent_state(data: dict):
    broadcast_event({"event": "agent_state", **data})


def on_agents_spawned(data: dict):
    broadcast_event({"event": "agents_spawned", **data})


def on_agents_update(data: dict):
    broadcast_event({"event": "agents_update", **data})


def on_action_required(data: dict):
    broadcast_event({"event": "action_required", **data})


def on_exfil_update(data: dict):
    broadcast_event({"event": "exfil_update", **data})


def on_phase_change(data: dict):
    broadcast_event({"event": "phase_change", **data})


def on_tick(data: dict):
    broadcast_event({"event": "tick", **data})


def on_agent_comm(data: dict):
    broadcast_event({"event": "agent_comm", **data})


def on_directive(data: dict):
    broadcast_event({"event": "directive", **data})


# Register event handlers
game_state.on("terminal", on_terminal)
game_state.on("agent_state", on_agent_state)
game_state.on("agents_spawned", on_agents_spawned)
game_state.on("agents_update", on_agents_update)
game_state.on("action_required", on_action_required)
game_state.on("exfil_update", on_exfil_update)
game_state.on("phase_change", on_phase_change)
game_state.on("tick", on_tick)
game_state.on("agent_comm", on_agent_comm)
game_state.on("directive", on_directive)


# --- REST Endpoints ---

@app.get("/api/status")
async def get_status():
    return {"status": "online", "phase": game_state.phase.value}


@app.get("/api/state")
async def get_state():
    return game_state.get_state()


# --- WebSocket Endpoint ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print(f"[WS] Client connected. Total: {len(connected_clients)}")

    # Send current state on connect
    try:
        await websocket.send_text(json.dumps({
            "event": "init",
            "state": game_state.get_state(),
        }))
    except Exception:
        pass

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_client_message(websocket, message)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "event": "error",
                    "text": "Invalid JSON received",
                }))
    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        print(f"[WS] Client disconnected. Total: {len(connected_clients)}")
    except Exception as e:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        print(f"[WS] Error: {e}")


async def handle_client_message(websocket: WebSocket, message: dict):
    """Handle incoming messages from the client."""
    msg_type = message.get("type", "")

    if msg_type == "start_directive":
        directive = message.get("directive", "").strip()
        if directive:
            game_state.phase = SwarmPhase.DIRECTIVE
            game_state.start_directive(directive)
        else:
            await websocket.send_text(json.dumps({
                "event": "error",
                "text": "Directive cannot be empty",
            }))

    elif msg_type == "authorize":
        action_id = str(message.get("action_id", ""))
        granted = message.get("granted", False)
        await game_state.authorize_action(action_id, granted)

    elif msg_type == "terminate_agent":
        agent_id = message.get("agent_id", "")
        game_state.terminate_agent(agent_id)

    elif msg_type == "deploy_countermeasure":
        game_state.deploy_countermeasure()

    elif msg_type == "cut_network":
        game_state.cut_network()

    elif msg_type == "ping":
        await websocket.send_text(json.dumps({"event": "pong"}))

    else:
        await websocket.send_text(json.dumps({
            "event": "error",
            "text": f"Unknown message type: {msg_type}",
        }))


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)