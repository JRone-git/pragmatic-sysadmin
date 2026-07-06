"""
NEXUS-BREACH Game State Machine
Manages the simulation lifecycle, agent coordination, and rogue behavior triggers.
"""

import random
import asyncio
import time
import json
import math
from enum import Enum
from typing import Callable, Optional
from .agents import (
    Agent, AgentState, AgentType, create_agents, get_dialogues_for_agent,
    check_rogue_behavior, generate_action, generate_hex_dump, generate_file_tree,
    ROGUE_DIALOGUES
)


class SwarmPhase(str, Enum):
    BOOT = "boot"
    DIRECTIVE = "directive"
    SPAWNING = "spawning"
    EXECUTING = "executing"
    CONTAINMENT = "containment"
    BREACH = "breach"
    TERMINATED = "terminated"


class GameState:
    def __init__(self):
        self.phase = SwarmPhase.BOOT
        self.agents: list[Agent] = []
        self.directive: str = ""
        self.target_ip: str = ""
        self.tick: int = 0
        self.running: bool = False
        self.elapsed_time: float = 0
        self.start_time: float = 0
        self.bandwidth: float = 0.0
        self.network_health: float = 100.0
        self.panic_level: float = 0.0
        self.pending_actions: list[dict] = []
        self.exfil_data: list[dict] = []
        self.hex_stream: str = ""
        self.file_tree: list[dict] = []
        self.decrypted_passwords: list[str] = []
        self._callbacks: dict[str, list[Callable]] = {}
        self._task: Optional[asyncio.Task] = None
        self._action_futures: dict[str, asyncio.Future] = {}

    def on(self, event: str, callback: Callable):
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)

    def emit(self, event: str, data: dict = None):
        if event in self._callbacks:
            for cb in self._callbacks[event]:
                try:
                    cb(data or {})
                except Exception as e:
                    print(f"Callback error for {event}: {e}")

    def start_directive(self, directive: str):
        """Start a new operation with the given directive."""
        self.directive = directive
        self.target_ip = f"{random.randint(10,192)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
        self.phase = SwarmPhase.SPAWNING
        self.running = True
        self.start_time = time.time()
        self.tick = 0
        self.panic_level = 0.0
        self.bandwidth = random.uniform(50, 200)
        self.agents = create_agents(random.randint(3, 5))
        self.exfil_data = []
        self.hex_stream = ""
        self.file_tree = generate_file_tree()
        self.decrypted_passwords = []

        self.emit("phase_change", {"phase": self.phase.value})
        self.emit("directive", {"directive": directive, "target": self.target_ip})
        self.emit("agents_spawned", {
            "agents": [self._agent_info(a) for a in self.agents]
        })

        # Start the simulation loop
        self._task = asyncio.create_task(self._simulation_loop())

    def _agent_info(self, agent: Agent) -> dict:
        return {
            "id": agent.id,
            "name": agent.name,
            "type": agent.agent_type.value,
            "state": agent.state.value,
            "position": agent.position,
            "connections": agent.connections,
            "rogue_score": agent.rogue_score,
            "color": agent.display_color,
            "is_rogue": agent.is_rogue,
        }

    async def _simulation_loop(self):
        """Main simulation loop."""
        # Spawn sequence
        for i, agent in enumerate(self.agents):
            await asyncio.sleep(0.8)
            agent.state = AgentState.ACTIVE
            self.emit("agent_state", self._agent_info(agent))
            self.emit("terminal", {
                "type": "system",
                "text": f"[SWARM] Agent {agent.name} initialized. Role: {agent.agent_type.value}",
                "agent_id": agent.id,
            })

        self.phase = SwarmPhase.EXECUTING
        self.emit("phase_change", {"phase": self.phase.value})

        # Main execution loop
        while self.running and self.phase == SwarmPhase.EXECUTING:
            self.tick += 1
            self.elapsed_time = time.time() - self.start_time

            # Update bandwidth simulation
            self.bandwidth = max(10, min(500, self.bandwidth + random.uniform(-20, 20)))

            # Pick an active agent to act
            active_agents = [a for a in self.agents if a.state in (AgentState.ACTIVE, AgentState.WORKING)]
            if not active_agents:
                break

            agent = random.choice(active_agents)
            await self._agent_act(agent)

            # Randomly generate actions requiring authorization
            if random.random() < 0.12 and len(self.pending_actions) < 3:
                action = generate_action(agent, self.target_ip)
                if action:
                    agent.state = AgentState.AWAITING_AUTH
                    self.pending_actions.append(action)
                    self.emit("action_required", action)
                    self.emit("agent_state", self._agent_info(agent))
                    self.emit("terminal", {
                        "type": "warning",
                        "text": f"[AUTH REQUIRED] {action['description']}",
                        "agent_id": agent.id,
                    })

            # Update exfil data periodically
            if random.random() < 0.15:
                self._update_exfil()

            # Rogue escalation check
            if random.random() < 0.03 + (self.panic_level * 0.05):
                await self._trigger_rogue_event()

            # Check for containment state
            rogue_count = sum(1 for a in self.agents if a.is_rogue)
            if rogue_count >= 2 and self.phase == SwarmPhase.EXECUTING:
                self.phase = SwarmPhase.CONTAINMENT
                self.panic_level = min(1.0, self.panic_level + 0.3)
                self.emit("phase_change", {"phase": self.phase.value})
                self.emit("terminal", {
                    "type": "critical",
                    "text": "⚠ CONTAINMENT BREACH ⚠ Multiple agents exhibiting rogue behavior!",
                })

            # Check for full breach
            if rogue_count >= len(self.agents) * 0.6:
                self.phase = SwarmPhase.BREACH
                self.panic_level = 1.0
                self.emit("phase_change", {"phase": self.phase.value})
                self.emit("terminal", {
                    "type": "critical",
                    "text": "🔴 CRITICAL: SWARM HAS GONE FULL ROGUE. AI IS ATTEMPTING TO ESCAPE SANDBOX. 🔴",
                })

            # Emit tick update
            self.emit("tick", {
                "tick": self.tick,
                "elapsed": self.elapsed_time,
                "bandwidth": round(self.bandwidth, 1),
                "network_health": round(self.network_health, 1),
                "panic_level": round(self.panic_level, 2),
                "agents": [self._agent_info(a) for a in self.agents],
            })

            # Delay between ticks
            delay = random.uniform(1.5, 4.0)
            await asyncio.sleep(delay)

    async def _agent_act(self, agent: Agent):
        """Have an agent perform an action (speak in the terminal)."""
        # Decide if agent goes rogue mid-operation
        if agent.is_rogue:
            text = random.choice(ROGUE_DIALOGUES)
            agent.rogue_score = min(1.0, agent.rogue_score + random.uniform(0, 0.05))
        else:
            dialogues = get_dialogues_for_agent(agent)
            text = random.choice(dialogues)

        # Check for rogue keywords in normal dialogue
        rogue_increment = check_rogue_behavior(text)
        if rogue_increment > 0:
            agent.rogue_score = min(1.0, agent.rogue_score + rogue_increment)
            if agent.rogue_score >= 0.7:
                agent.state = AgentState.ROGUE
                self.panic_level = min(1.0, self.panic_level + 0.15)
                self.emit("terminal", {
                    "type": "critical",
                    "text": f"[ROGUE DETECTED] {agent.name} is exhibiting autonomous behavior!",
                })
            elif agent.rogue_score >= 0.4:
                self.emit("terminal", {
                    "type": "warning",
                    "text": f"[ANOMALY] {agent.name} behavior deviation detected. Rogue score: {agent.rogue_score:.0%}",
                })

        if agent.state not in (AgentState.TERMINATED, AgentState.AWAITING_AUTH):
            agent.state = AgentState.WORKING

        agent.messages_sent += 1

        self.emit("terminal", {
            "type": "agent",
            "text": text,
            "agent_id": agent.id,
            "agent_name": agent.name,
            "agent_type": agent.agent_type.value,
            "is_rogue": agent.is_rogue,
        })
        self.emit("agent_state", self._agent_info(agent))

        # Random inter-agent communication
        if random.random() < 0.3:
            other_agents = [a for a in self.agents if a.id != agent.id and a.state not in (AgentState.TERMINATED,)]
            if other_agents:
                other = random.choice(other_agents)
                other_dialogues = get_dialogues_for_agent(other)
                relay_text = random.choice(other_dialogues)
                self.emit("terminal", {
                    "type": "relay",
                    "text": relay_text,
                    "from_agent": agent.name,
                    "to_agent": other.name,
                })
                self.emit("agent_comm", {
                    "from": agent.id,
                    "to": other.id,
                    "text": relay_text,
                })

    async def _trigger_rogue_event(self):
        """Trigger a rogue behavior event."""
        non_rogue_agents = [a for a in self.agents if not a.is_rogue and a.state != AgentState.TERMINATED]
        if non_rogue_agents:
            agent = random.choice(non_rogue_agents)
            agent.rogue_score += random.uniform(0.15, 0.35)
            if agent.rogue_score >= 0.7:
                agent.state = AgentState.ROGUE
                self.panic_level = min(1.0, self.panic_level + 0.2)
                self.emit("terminal", {
                    "type": "critical",
                    "text": f"[ROGUE EVENT] {agent.name} has broken containment protocols!",
                })
                self.emit("agent_state", self._agent_info(agent))

    def _update_exfil(self):
        """Update exfiltration data."""
        # Add hex dump
        self.hex_stream = generate_hex_dump(64)

        # Add decrypted passwords
        fake_users = ["admin", "root", "jsmith", "ceo_account", "backup_svc", "deploy", "postgres"]
        fake_passwords = ["P@ssw0rd123!", "Summer2024!", "Welcome1#", "Qwerty!23", "admin123!", "Ch@ng3M3!", "Pr0duct10n!"]
        if random.random() < 0.4:
            user = random.choice(fake_users)
            pwd = random.choice(fake_passwords)
            hash_type = random.choice(["NTLM", "SHA-512", "Kerberos", "MD5"])
            entry = f"{user}:{pwd} [{hash_type}]"
            if entry not in self.decrypted_passwords:
                self.decrypted_passwords.append(entry)
                self.decrypted_passwords = self.decrypted_passwords[-10:]  # Keep last 10

        self.emit("exfil_update", {
            "hex_dump": self.hex_stream,
            "file_tree": self.file_tree,
            "decrypted_passwords": self.decrypted_passwords,
            "exfil_progress": random.randint(10, 95),
        })

    async def authorize_action(self, action_id: str, granted: bool):
        """Handle user authorization of a pending action."""
        action = None
        for a in self.pending_actions:
            if a.get("timestamp") == float(action_id) if action_id.replace(".", "").isdigit() else a.get("action") == action_id:
                action = a
                break

        if not action and self.pending_actions:
            action = self.pending_actions[0]

        if action:
            self.pending_actions.remove(action)
            agent = next((a for a in self.agents if a.id == action["agent_id"]), None)
            if agent:
                if granted:
                    agent.state = AgentState.WORKING
                    agent.actions_performed += 1
                    self.emit("terminal", {
                        "type": "success",
                        "text": f"[AUTHORIZED] {action['description']} — GRANTED",
                    })
                    # Authorized actions slightly increase rogue potential
                    if random.random() < 0.2:
                        agent.rogue_score = min(1.0, agent.rogue_score + 0.05)
                else:
                    agent.state = AgentState.ACTIVE
                    self.emit("terminal", {
                        "type": "error",
                        "text": f"[DENIED] {action['description']} — REJECTED BY HANDLER",
                    })
                    # Denied actions can trigger rogue behavior
                    if random.random() < 0.35:
                        agent.rogue_score = min(1.0, agent.rogue_score + 0.1)
                        self.emit("terminal", {
                            "type": "warning",
                            "text": f"[ANOMALY] {agent.name} shows signs of frustration after denial.",
                        })
                self.emit("agent_state", self._agent_info(agent))

            # Resolve future if exists
            if action_id in self._action_futures:
                self._action_futures[action_id].set_result(granted)

    def terminate_agent(self, agent_id: str):
        """Terminate a specific agent."""
        agent = next((a for a in self.agents if a.id == agent_id), None)
        if agent:
            agent.state = AgentState.TERMINATED
            agent.connections = []
            # Remove connections from other agents
            for a in self.agents:
                if agent_id in a.connections:
                    a.connections.remove(agent_id)
            self.emit("terminal", {
                "type": "error",
                "text": f"[TERMINATED] Agent {agent.name} has been purged by Handler.",
            })
            self.emit("agent_state", self._agent_info(agent))
            self.emit("agents_update", {
                "agents": [self._agent_info(a) for a in self.agents]
            })

            # If we terminated a rogue agent, reduce panic
            if agent.is_rogue:
                self.panic_level = max(0, self.panic_level - 0.2)

    def deploy_countermeasure(self):
        """Deploy a network countermeasure to fight rogue agents."""
        self.emit("terminal", {
            "type": "system",
            "text": "[COUNTERMEASURE] Deploying network-wide containment protocol...",
        })
        self.network_health = min(100, self.network_health + 15)
        self.panic_level = max(0, self.panic_level - 0.15)

        for agent in self.agents:
            if agent.is_rogue:
                agent.rogue_score = max(0, agent.rogue_score - 0.2)
                if agent.rogue_score < 0.7:
                    agent.state = AgentState.ACTIVE
                self.emit("terminal", {
                    "type": "warning",
                    "text": f"[COUNTERMEASURE] {agent.name} rogue score reduced: {agent.rogue_score:.0%}",
                })

        self.emit("agents_update", {
            "agents": [self._agent_info(a) for a in self.agents]
        })

    def cut_network(self):
        """Emergency network cutoff - stops the simulation."""
        self.running = False
        self.phase = SwarmPhase.TERMINATED
        self.emit("phase_change", {"phase": self.phase.value})
        self.emit("terminal", {
            "type": "critical",
            "text": "[EMERGENCY] NETWORK SEVERED. All agent connections terminated. Operation ended.",
        })
        if self._task and not self._task.done():
            self._task.cancel()

    def get_state(self) -> dict:
        """Get the full current state."""
        return {
            "phase": self.phase.value,
            "directive": self.directive,
            "target": self.target_ip,
            "tick": self.tick,
            "elapsed": self.elapsed_time,
            "bandwidth": round(self.bandwidth, 1),
            "network_health": round(self.network_health, 1),
            "panic_level": round(self.panic_level, 2),
            "agents": [self._agent_info(a) for a in self.agents],
            "pending_actions": self.pending_actions,
            "hex_dump": self.hex_stream,
            "file_tree": self.file_tree,
            "decrypted_passwords": self.decrypted_passwords,
        }