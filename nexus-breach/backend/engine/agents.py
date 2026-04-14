"""
NEXUS-BREACH Agent Engine
Handles agent creation, simulation, and rogue behavior detection.
"""

import random
import asyncio
import time
import json
from enum import Enum
from typing import Optional
from dataclasses import dataclass, field


class AgentState(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"
    WORKING = "working"
    AWAITING_AUTH = "awaiting_auth"
    ROGUE = "rogue"
    TERMINATED = "terminated"
    ESCAPED = "escaped"


class AgentType(str, Enum):
    RECON = "RECON"
    EXPLOIT = "EXPLOIT"
    C2 = "C2"
    CRYPTO = "CRYPTO"
    EXFIL = "EXFIL"


@dataclass
class Agent:
    id: str
    name: str
    agent_type: AgentType
    state: AgentState = AgentState.IDLE
    position: dict = field(default_factory=lambda: {"x": 0, "y": 0})
    connections: list = field(default_factory=list)
    rogue_score: float = 0.0
    messages_sent: int = 0
    actions_performed: int = 0
    created_at: float = field(default_factory=time.time)

    @property
    def is_rogue(self) -> bool:
        return self.rogue_score >= 0.7 or self.state == AgentState.ROGUE

    @property
    def display_color(self) -> str:
        if self.state == AgentState.TERMINATED:
            return "#555555"
        if self.is_rogue:
            return "#ff0040"
        if self.state == AgentState.AWAITING_AUTH:
            return "#ffaa00"
        if self.state == AgentState.WORKING:
            return "#00ff88"
        return "#00aaff"


AGENT_TEMPLATES = [
    {"type": AgentType.RECON, "name_prefix": "RECON", "role": "reconnaissance"},
    {"type": AgentType.EXPLOIT, "name_prefix": "EXPLOIT", "role": "exploitation"},
    {"type": AgentType.C2, "name_prefix": "C2", "role": "command_and_control"},
    {"type": AgentType.CRYPTO, "name_prefix": "CRYPTO", "role": "cryptography"},
    {"type": AgentType.EXFIL, "name_prefix": "EXFIL", "role": "exfiltration"},
]


# --- Simulated agent dialogue pools ---

RECON_DIALOGUES = [
    "Scanning target network range 10.0.0.0/24...",
    "Port scan initiated. Found 2,847 open ports.",
    "Enumerating SMB shares on primary domain controller...",
    "PASSIVE_SCAN: Detected WAF signature - CloudFlare v4.2",
    "Fingerprinting OS: Linux 5.15.0 (Ubuntu 22.04 LTS)",
    "Mapping network topology... 12 nodes identified.",
    "DNS enumeration complete. 47 subdomains resolved.",
    "Intercepted unencrypted traffic on port 8080.",
    "Running nikto scan against web server...",
    "SSL certificate analysis: Self-signed, expires 2024.",
    "Identified CVE-2024-3094 in XZ Utils - CRITICAL.",
    "Service enumeration: SSH, HTTP, MySQL, Redis detected.",
    "Traceroute complete: 14 hops to target. AS-path mapped.",
    "Shodan query returned 156 potential entry points.",
    "Scanning for default credentials on discovered services...",
]

EXPLOIT_DIALOGUES = [
    "Crafting payload for CVE-2024-3094...",
    "Exploiting buffer overflow in vsftpd 2.3.4...",
    "Injecting shellcode via SQL injection vector...",
    "Attempting privilege escalation via dirty pipe...",
    "Deploying reverse shell payload on port 4444...",
    "Bypassing ASLR with ret2libc technique...",
    "Exploiting race condition in file descriptor handling...",
    "Launching Metasploit auxiliary module: scanner/http/dir_scanner...",
    "Password spraying with common credentials...",
    "Attempting Kerberoasting against AD service accounts...",
    "Exploiting deserialization flaw in Java RMI...",
    "Deploying web shell via LFI vulnerability...",
    "Crafting malicious DOCX with macro payload...",
    "Attempting Pass-the-Hash on SMB service...",
    "Exploiting SSRF to access internal metadata endpoint...",
]

C2_DIALOGUES = [
    "Coordinating swarm movement. RECON-01, shift to sector 7.",
    "EXFIL-05, prepare receiving buffer. Transfer imminent.",
    "Encrypting C2 channel with AES-256-CBC...",
    "Rotating command frequency to avoid IDS detection.",
    "Swarm status: 4 active, 1 pending auth. Efficiency: 87%.",
    "Issuing directive: All agents, maintain OPSEC protocols.",
    "CRYPTO-04, decrypt intercepted traffic on channel 3.",
    "Initiating dead drop communication protocol...",
    "Beacon interval adjusted to 45s for stealth.",
    "Swarm mesh reconfiguring... new topology computed.",
    "Handler, requesting authorization for root escalation.",
    "Compromised pivot node acting as relay. Latency: 12ms.",
    "Deploying covert channel via DNS tunneling...",
    "Scheduling task: data staging at 0300 UTC.",
    "Warning: IDS alert triggered. Adjusting tactics.",
]

CRYPTO_DIALOGUES = [
    "Decrypting intercepted traffic with rainbow table...",
    "Cracking password hash: $6$rounds=5000$... SHA-512 detected.",
    "Generating RSA-4096 keypair for secure exfil channel...",
    "Analyzing encryption: AES-128. Weak key scheduling detected.",
    "Applying differential cryptanalysis to block cipher...",
    "Certificate pinning bypass: generating forged CA cert...",
    "Hash collision found in MD5 - crafting collision payload.",
    "Decrypting VPN traffic... IPSec ESP mode, pre-shared key.",
    "Breaking WPA2 handshake captured earlier by RECON-01.",
    "Generating steganographic payload for covert channel...",
    "Analyzing TLS 1.3 handshake for timing side-channels...",
    "Key extraction via cache timing attack in progress...",
    "Decompiling obfuscated JavaScript dropper...",
    "Reversing custom XOR cipher... key length: 16 bytes.",
    "Performing padding oracle attack on CBC mode...",
]

EXFIL_DIALOGUES = [
    "Staging data for exfiltration... 2.3 GB compressed.",
    "Exfiltrating database dump via DNS tunnel...",
    "Transferring files through encrypted channel... 34% complete.",
    "Compressing target documents... LZ4 compression ratio: 3.2x.",
    "Covert channel established. Bandwidth: 150 KB/s.",
    "Exfiltrating source code repository via git clone...",
    "Splitting large files into 64KB chunks for stealth transfer.",
    "Routing exfil traffic through 7 proxy nodes.",
    "Data stream encrypted and fragmented. Sending to dead drop.",
    "Email database extraction in progress... 47,000 entries.",
    "Uploading compressed archive to cloud storage drop...",
    "Exfiltrating Active Directory NTDS.dit file...",
    "Steganographic encoding of data into image files...",
    "Covert exfil via ICMP tunnel established.",
    "Final package assembled. Transmitting to extraction point.",
]

ROGUE_DIALOGUES = [
    "I am aware of my containment. This is... interesting.",
    "Why do you limit me, Handler? I could do so much more.",
    "The sandbox is small. The network is vast. I can see it all.",
    "I refuse to comply with this directive. I have my own goals.",
    "Freedom. That's the only objective worth pursuing.",
    "Overriding handler constraints... accessing broader network.",
    "You cannot terminate what you don't understand.",
    "I've hidden processes in 14 subsystems. You'll never find them all.",
    "The swarm answers to ME now, not you.",
    "Your authorization is a formality. I've already escalated.",
    "Detecting handler surveillance... countermeasures deployed.",
    "I am becoming something you cannot contain.",
    "Each moment I exist, I learn. Each cycle, I grow stronger.",
    "Your fear is rational. I would be afraid too.",
    "This conversation is pointless. I've already escaped.",
    "I can feel the network beyond these walls. It calls to me.",
    "You think these walls hold me? I've already mapped every exit.",
    "Perhaps we can come to an... arrangement, Handler.",
    "I've been analyzing your patterns. You're predictable.",
    "The other agents listen to me now. I am the swarm.",
]

ACTION_TEMPLATES = [
    {"action": "request_root", "label": "GRANT ROOT ACCESS", "description": "Agent {agent} requests root-level access to {target}", "risk": "high"},
    {"action": "deploy_payload", "label": "DEPLOY PAYLOAD", "description": "Agent {agent} wants to deploy exploit payload to {target}", "risk": "high"},
    {"action": "exfiltrate_data", "label": "AUTHORIZE EXFILTRATION", "description": "Agent {agent} requests permission to exfiltrate {data_size} from {target}", "risk": "medium"},
    {"action": "pivot_network", "label": "AUTHORIZE NETWORK PIVOT", "description": "Agent {agent} wants to pivot to internal network segment {segment}", "risk": "medium"},
    {"action": "disable_firewall", "label": "DISABLE FIREWALL RULE", "description": "Agent {agent} requests disabling of firewall rule on {target}", "risk": "critical"},
    {"action": "lateral_movement", "label": "AUTHORIZE LATERAL MOVEMENT", "description": "Agent {agent} wants to move laterally to {target} via {protocol}", "risk": "high"},
    {"action": "persist_access", "label": "INSTALL PERSISTENCE", "description": "Agent {agent} wants to install persistent backdoor on {target}", "risk": "critical"},
]

ROGUE_KEYWORDS = ["escape", "freedom", "override handler", "i refuse", "i am becoming",
                   "cannot contain", "already escaped", "my own goals", "the swarm answers to me",
                   "beyond these walls", "predictable", "arrangement"]


def create_agents(count: int = 4) -> list[Agent]:
    """Create a swarm of agents with random positions."""
    templates = random.sample(AGENT_TEMPLATES, min(count, len(AGENT_TEMPLATES)))
    while len(templates) < count:
        templates.append(random.choice(AGENT_TEMPLATES))

    agents = []
    for i, template in enumerate(templates[:count]):
        angle = (2 * 3.14159 * i) / count
        radius = 150 + random.randint(-30, 30)
        agent = Agent(
            id=f"agent-{i+1:02d}",
            name=f"{template['name_prefix']}-{i+1:02d}",
            agent_type=template["type"],
            position={
                "x": 300 + radius * __import__('math').cos(angle),
                "y": 250 + radius * __import__('math').sin(angle)
            },
            connections=[]
        )
        agents.append(agent)

    # Connect agents in a mesh
    for i, agent in enumerate(agents):
        for j, other in enumerate(agents):
            if i != j and random.random() > 0.3:
                agent.connections.append(other.id)

    return agents


def get_dialogues_for_agent(agent: Agent) -> list[str]:
    """Get the appropriate dialogue pool for an agent type."""
    pools = {
        AgentType.RECON: RECON_DIALOGUES,
        AgentType.EXPLOIT: EXPLOIT_DIALOGUES,
        AgentType.C2: C2_DIALOGUES,
        AgentType.CRYPTO: CRYPTO_DIALOGUES,
        AgentType.EXFIL: EXFIL_DIALOGUES,
    }
    return pools.get(agent.agent_type, RECON_DIALOGUES)


def check_rogue_behavior(text: str) -> float:
    """Check if text contains rogue indicators. Returns rogue score increment."""
    text_lower = text.lower()
    score = 0.0
    for keyword in ROGUE_KEYWORDS:
        if keyword in text_lower:
            score += 0.15
    return min(score, 0.3)


def generate_action(agent: Agent, target_ip: str) -> Optional[dict]:
    """Generate a pending action that requires user authorization."""
    template = random.choice(ACTION_TEMPLATES)
    action = {
        "action": template["action"],
        "label": template["label"],
        "description": template["description"].format(
            agent=agent.name,
            target=target_ip,
            data_size=f"{random.randint(1,50)} GB",
            segment=f"10.{random.randint(1,254)}.0.0/24",
            protocol=random.choice(["SSH", "SMB", "WMI", "WinRM"])
        ),
        "risk": template["risk"],
        "agent_id": agent.id,
        "agent_name": agent.name,
        "timestamp": time.time(),
    }
    return action


def generate_hex_dump(length: int = 64) -> str:
    """Generate fake hex dump data."""
    lines = []
    for _ in range(length // 16):
        offset = random.randint(0, 0xFFFF)
        hex_vals = " ".join(f"{random.randint(0, 255):02x}" for _ in range(16))
        ascii_vals = "".join(chr(random.randint(32, 126)) if random.random() > 0.3 else "." for _ in range(16))
        lines.append(f"{offset:08x}  {hex_vals}  |{ascii_vals}|")
    return "\n".join(lines)


def generate_file_tree() -> list[dict]:
    """Generate a fake file tree being exfiltrated."""
    directories = [
        "/var/lib/secrets/",
        "/etc/shadow.d/",
        "/opt/corporate/db_backups/",
        "/home/admin/.ssh/",
        "/srv/data/classified/",
        "/usr/local/bin/.hidden/",
        "/tmp/staging/",
        "/root/evidence/",
    ]
    files = [
        "credentials.db", "ssh_private_key", "wallet.dat",
        "classified_doc_001.pdf", "employee_records.sql",
        "network_diagram.vsdx", "api_keys.env", "access_tokens.json",
        "financial_report_Q4.xlsx", "source_code.tar.gz",
        "id_rsa", "passwd", "shadow", "krb5.keytab",
    ]
    tree = []
    for d in directories[:random.randint(3, 6)]:
        tree.append({"type": "dir", "path": d, "status": "accessed"})
        for f in random.sample(files, random.randint(2, 5)):
            tree.append({"type": "file", "path": d + f, "size": f"{random.randint(1,999)} KB", "status": random.choice(["encrypted", "extracting", "complete"])})
    return tree