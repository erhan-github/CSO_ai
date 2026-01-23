"""
Side Server - Sidelith Strategic Intelligence.

This module implements the stdio-based MCP server that responds to tool calls
from Cursor and other MCP-compatible clients.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    PromptMessage,
    TextContent,
    Tool,
    Resource,
)

from side.logging_config import setup_logging
from side.tools import TOOLS, handle_tool_call
from side.services.service_manager import ServiceManager


def load_env_file() -> None:
    """Load environment variables from .env file."""
    # Check multiple possible locations (in priority order)
    possible_paths = [
        # Project root (side-mcp/.env) - most likely location
        Path(__file__).parent.parent.parent / ".env",
        # Current working directory
        Path.cwd() / ".env",
        # Parent of cwd (if running from src/)
        Path.cwd().parent / ".env",
        # User config directory
        Path.home() / ".side-mcp" / ".env",
    ]

    for env_path in possible_paths:
        try:
            env_path = env_path.expanduser().resolve()
            if env_path.exists():
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip().strip("'\"")
                            if key and value and key not in os.environ:
                                os.environ[key] = value
                break  # Use first found .env
        except Exception:
            continue
    
    # [Hyper-Ralph] Scenario 61 Fix: Insecure Env Loading
    # Verify .env permissions (should be 600 or 400)
    dotenv_path = Path(".env")
    if dotenv_path.exists():
        import stat
        mode = dotenv_path.stat().st_mode
        if mode & stat.S_IRGRP or mode & stat.S_IROTH:
            logger.warning("⚠️ SECURITY WARNING: .env file is world-readable (mode %o). Recommend 'chmod 600 .env'.", mode & 0o777)



# Load environment variables before anything else
load_env_file()

# Configure comprehensive logging
# Get log level from environment or default to INFO
log_level = os.getenv("SIDE_LOG_LEVEL", "INFO")
setup_logging(log_level=log_level)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("side-mcp")

# Create MCP server instance
server = Server("side")

# -----------------------------------------------------------------------------
# GLOBAL SERVICE INITIALIZATION
# -----------------------------------------------------------------------------
from side.intel.memory import MemoryPersistence, MemoryManager, MemoryRetrieval
from side.services.memory_interceptor import MemoryInterceptor
from side.llm.client import LLMClient

from side.tools.forensics_tool import ForensicsTool

# Initialize Memory System Globally
# This ensures all handlers use the same instances
MEMORY_PATH = Path.home() / ".side" / "memory"
_llm_client = LLMClient()
_memory_persistence = MemoryPersistence(MEMORY_PATH)
_memory_manager = MemoryManager(_memory_persistence, _llm_client)
_memory_retrieval = MemoryRetrieval(_memory_persistence, _llm_client)
_memory_interceptor = MemoryInterceptor(_memory_manager)
_memory_maintenance = MemoryMaintenance(_memory_persistence, _llm_client)

# Initialize Forensics
_forensics_tool = ForensicsTool(Path.cwd())

# Dynamic Prompt Manager
from side.storage.simple_db import SimplifiedDatabase
from side.intel.intelligence_store import IntelligenceStore

class DynamicPromptManager:
    def __init__(self):
        # Initialize DB connection for reading findings
        try:
            db_path = Path.home() / ".side" / "local.db"
            self.db = SimplifiedDatabase(db_path)
            self.store = IntelligenceStore(self.db)
            self.project_path = Path.cwd()
            self.project_id = SimplifiedDatabase.get_project_id(self.project_path)
        except Exception:
            self.store = None

    def get_prompts(self) -> list[Prompt]:
        prompts = [

            Prompt(
                name="strategy",
                description="Get strategic advice - 'What should I focus on?'",
                arguments=[
                    PromptArgument(
                        name="context",
                        description="Optional context about what you're working on",
                        required=False,
                    ),
                ],
            ),
        ]
        
        if not self.store:
            return prompts

        try:
            # Fetch active high-severity findings
            findings = self.store.get_active_findings(self.project_id)
            
            # Group by type to avoid spamming prompts
            security_issues = [f for f in findings if f['severity'] in ['CRITICAL', 'HIGH'] and f.get('metadata', {}).get('dimension') == 'Security']
            perf_issues = [f for f in findings if f['severity'] in ['CRITICAL', 'HIGH'] and f.get('metadata', {}).get('dimension') == 'Performance']
            
            if security_issues:
                prompts.append(Prompt(
                    name="fix-security-critical",
                    description=f"🚨 Fix {len(security_issues)} Critical Security Issues (Auth, Secrets, etc.)",
                    arguments=[]
                ))
            
            # [Level 3 Interaction: fix_flow]
            if findings:
                prompts.append(Prompt(
                    name="fix_flow",
                    description="✨ Smart Fix: Auto-resolves the most pressing issue found.",
                    arguments=[]
                ))
            
            # [Experience V2: The CSO Briefing]
            prompts.append(Prompt(
                name="brief",
                description="☀️ Mission Briefing: Strategic status, recent work, and today's focus.",
                arguments=[]
            ))
            
            # [Experience V2: The CSO Consult]
            prompts.append(Prompt(
                name="consult",
                description="🧠 Strategic Consultation: Get a CTO-level decision on a technical or business choice.",
                arguments=[
                     PromptArgument(
                        name="question",
                        description="The strategic question (e.g., 'Should we switch to Next.js?')",
                        required=True,
                    ),
                ]
            ))
            
            # [Experience V2: The CSO Gatekeeper]
            prompts.append(Prompt(
                name="verify",
                description="🛡️ Pre-Flight Check: Verify system health before shipping/deploying.",
                arguments=[]
            ))
            
            # [Experience V3: The Frontend Guard]
            prompts.append(Prompt(
                name="check_design",
                description="🎨 Design System Guard: Enforce UI consistency and prevent ad-hoc styling.",
                arguments=[
                    PromptArgument(
                        name="code",
                        description="The code snippet or file content to review.",
                        required=True,
                    )
                ]
            ))
            
            # [Experience V3: The Truth Engine]
            prompts.append(Prompt(
                name="check_truth",
                description="🔍 Truth Engine: Verify that documentation (README, Vision) matches reality.",
                arguments=[]
            ))

            # [Experience V4: Deep Forensics]
            prompts.append(Prompt(
                name="audit_deep",
                description="🕵️ Deep Recursive Audit: Scan codebase for complex patterns (e.g. 'hardcoded secrets').",
                arguments=[
                    PromptArgument(
                        name="query",
                        description="What to look for (e.g. 'security vulnerabilities' or 'unused code')",
                        required=True,
                    )
                ]
            ))
            
            if perf_issues:
                prompts.append(Prompt(
                    name="fix-performance-critical",
                    description=f"⚡ Fix {len(perf_issues)} Performance bottlenecks (N+1 queries, loops)",
                    arguments=[]
                ))
                
        except Exception as e:
            logger.error(f"Failed to load dynamic prompts: {e}")
            
        return prompts

    def get_prompt_result(self, name: str, args: dict[str, str]) -> GetPromptResult:
        if name == "fix_flow":
            # Smart Logic: Find the worst issue
            findings = self.store.get_active_findings(self.project_id)
            if not findings:
                 return GetPromptResult(
                    description="No issues found",
                    messages=[PromptMessage(role="user", content=TextContent(type="text", text="Side, run a deep audit to find new things to fix."))]
                )
            
            # Sort by severity (CRITICAL > HIGH > MEDIUM > LOW)
            severity_map = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
            findings.sort(key=lambda x: severity_map.get(x.get('severity', 'INFO'), 5))
            top_issue = findings[0]
            
            return GetPromptResult(
                description=f"Fix: {top_issue.get('message', 'Issue')}",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Side, fix this {top_issue.get('severity')} issue:\n\n"
                                 f"**Issue**: {top_issue.get('message')}\n"
                                 f"**File**: {top_issue.get('file_path')}\n"
                                 f"**Fix**: Analyze the code and apply a robust patch.\n"
                                 f"**Verify**: Ensure tests pass after fixing."
                        ),
                    ),
                ],
            )
            
        if name == "brief":
            # 1. Get Profile
            profile = self.db.get_profile(self.project_id) or {}
            
            # 2. Get Active Plans
            all_plans = self.db.list_plans()
            active = [p for p in all_plans if p.get('status') == 'active']
            top_focus = active[0]['title'] if active else "No active directives."
            
            # 3. Get Recent Activity (Context)
            activities = self.db.get_recent_activities(self.project_id, limit=5)
            recent_context = "\n".join([f"- {a['action']} ({a['tool']})" for a in activities]) if activities else "None."
            
            return GetPromptResult(
                description="Mission Briefing",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Side, give me a Strategic Mission Briefing.\n\n"
                                 f"**Pilot**: {profile.get('name', 'Founder')} ({profile.get('tier', 'free').upper()})\n"
                                 f"**Current Focus**: {top_focus}\n"
                                 f"**Recent Context**:\n{recent_context}\n\n"
                                 f"**Goal**: Analyze my recent context and tell me exactly what I should do next to advance the Focus. Be concise and strategic."
                        ),
                    ),
                ],
            )

        if name == "consult":
            question = args.get("question", "What should we do?")
            
            # 1. Get Strategic Context
            profile = self.db.get_profile(self.project_id) or {}
            stack = profile.get("tech_stack", "Unknown Stack")
            stage = profile.get("stage", "Unknown Stage")
            
            # 2. Get Past Decisions (Consistency)
            # We don't have a direct get_recent_decisions method exposed in SimpleDB wrapper effectively,
            # but we can query raw.
            with self.db._connection() as conn:
                rows = conn.execute(
                    "SELECT question, answer, category FROM decisions WHERE project_id = ? ORDER BY created_at DESC LIMIT 3", 
                    (self.project_id,)
                ).fetchall()
                past_decisions = "\n".join([f"- Q: {r['question']} -> A: {r['answer']}" for r in rows]) if rows else "None."

            return GetPromptResult(
                description="Strategic Consultation",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Side, I need a CTO-level decision.\n\n"
                                 f"**Question**: \"{question}\"\n\n"
                                 f"**Context**:\n"
                                 f"- **Stage**: {stage}\n"
                                 f"- **Stack**: {stack}\n"
                                 f"- **Precedent** (Last 3 Decisions):\n{past_decisions}\n\n"
                                 f"**Directives**:\n"
                                 f"1. Analyze the trade-offs (Cost, Speed, Debt).\n"
                                 f"2. Check alignment with our Stage (e.g. don't over-engineer for MVP).\n"
                                 f"3. Give a Verdict: **YES/NO/DEFER**.\n"
                                 f"4. Provide a 1-sentence Strategic Rationale."
                        ),
                    ),
                ],
            )

        if name == "verify":
            # 1. Get Security Posture
            summary = self.db.get_audit_summary(self.project_id)
            crit = summary.get("CRITICAL", 0)
            high = summary.get("HIGH", 0)
            
            # 2. Get Recent Work
            # Determine what to verify (e.g. files changed recently, though we can't easily get diffs here without git tool)
            # We'll ask the Agent to check Logic and Security.
            
            status = "🔴 BLOCKED" if crit > 0 else ("🟠 RISKY" if high > 0 else "🟢 CLEAR")
            
            return GetPromptResult(
                description="Pre-Flight Verification",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Side, Perform a Pre-Flight Verification.\n\n"
                                 f"**Current Status**: {status}\n"
                                 f"- Critical Issues: {crit}\n"
                                 f"- High Issues: {high}\n\n"
                                 f"**Protocol**:\n"
                                 f"1. Run `audit` on any modified files.\n"
                                 f"2. Verify no 'print' debugging or secrets are left.\n"
                                 f"3. Confirm compliance with the Active Plan.\n"
                                 f"4. Verdict: **SHIP IT** or **BLOCK**."
                        ),
                    ),
                ],
            )

        if name == "check_design":
            code_snippet = args.get("code", "")
            
            # 1. Discover Design System
            web_root = self.project_path / "web"
            components = []
            if web_root.exists():
                # Naive scan for components/ui or components
                ui_dir = web_root / "components"
                if ui_dir.exists():
                     # Recursively find .tsx files
                     for f in ui_dir.rglob("*.tsx"):
                         if not f.name.startswith("index"):
                             components.append(f.stem)
            
            component_list = ", ".join(sorted(components)) or "None detected."

            return GetPromptResult(
                description="Design System Review",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Side, review this frontend code for Design System compliance.\n\n"
                                 f"**Approved Components**: [{component_list}]\n\n"
                                 f"**Code to Review**:\n```tsx\n{code_snippet}\n```\n\n"
                                 f"**Directives**:\n"
                                 f"1. Identify unauthorized HTML elements (e.g. `button`, `input`) that should be Reusable Components.\n"
                                 f"2. Identify hardcoded CSS/Tailwind that duplicates Design System tokens.\n"
                                 f"3. Rewrite the code to use the Approved Components."
                        ),
                    ),
                ],
            )

        if name == "check_truth":
            # 1. Discover Strategy Docs
            docs_context = ""
            for doc_name in ["README.md", "backend/VISION.md", "docs/MASTER_ROADMAP.md"]:
                doc_path = self.project_path / doc_name
                if doc_path.exists():
                     content = doc_path.read_text()
                     # Extract first 1000 chars to avoid prompt overflow but give enough context
                     docs_context += f"\n--- {doc_name} ---\n{content[:1000]}...\n"
            
            if not docs_context:
                docs_context = "No strategic documentation found (README.md, VISION.md, etc.)."

            return GetPromptResult(
                description="Strategic Reality Check",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Side, Perform a Strategic Reality Check (Truth Engine).\n\n"
                                 f"**Documentation Context**:\n{docs_context}\n\n"
                                 f"**Directives**:\n"
                                 f"1. Identify every 'Feature Claim' or 'Strategic Goal' mentioned in the docs.\n"
                                 f"2. Verify if the code for these features actually exists in the monorepo.\n"
                                 f"3. Identify Omissions (Built but not Doc'd) or Hallucinations (Doc'd but not Built).\n"
                                 f"4. Report 'Documentation Debt' as a list of actionable tasks."
                        ),
                    ),
                ],
            )
            
        if name == "fix-security-critical":
            return GetPromptResult(
                description="Fix Critical Security Issues",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text="Hey Side, list all critical/high security issues. For each one:\n1. Explain the risk.\n2. Propose a code fix.\n3. Apply the fix.\n4. Call `verify_fix` to confirm resolution.\n\nCRITICAL: If `verify_fix` fails, you MUST attempt a different fix and verify again. Do NOT report back until the fix is verified as PASS.",
                        ),
                    ),
                ],
            )
        
        if name == "fix-performance-critical":
            return GetPromptResult(
                description="Fix Critical Performance Issues",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text="Hey Side, identify the top performance bottlenecks. Focus on N+1 queries and expensive loops. optimize them and verify the speedup.",
                        ),
                    ),
                ],
            )
            
        # Default handlers

            
        if name == "strategy":
            context = args.get('context', '')
            return GetPromptResult(
                description=f"Strategic advice{f' for {context}' if context else ''}",
                messages=[PromptMessage(role="user", content=TextContent(type="text", text=f"Side, what should I focus on?{f' Context: {context}' if context else ''}"))],
            )
            
        raise ValueError(f"Unknown prompt: {name}")

prompt_manager = DynamicPromptManager()

@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    """Return the list of available prompts."""
    return prompt_manager.get_prompts()

@server.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    """Handle prompt requests."""
    return prompt_manager.get_prompt_result(name, arguments or {})


# -----------------------------------------------------------------------------
# RESOURCE MANAGER (The "Eyes")
# -----------------------------------------------------------------------------
class ResourceManager:
    def __init__(self):
        try:
            db_path = Path.home() / ".side" / "local.db"
            self.db = SimplifiedDatabase(db_path)
        except Exception:
            self.db = None

    def list_resources(self) -> list[Resource]:
        return [
            Resource(
                uri="side://monolith",
                name="Strategic Monolith",
                description="The live dashboard of project status, tasks, and credits.",
                mimeType="text/markdown"
            ),
            Resource(
                uri="side://activity",
                name="Activity Log (Live)",
                description="Recent system actions, costs, and traces.",
                mimeType="application/json"
            ),
            Resource(
                uri="side://profile",
                name="Pilot Profile",
                description="User stats, level, tech stack, and tier.",
                mimeType="application/json"
            ),
            Resource(
                uri="side://tips",
                name="Daily Intel",
                description="Strategic tips and system hacks.",
                mimeType="text/plain"
            )
        ]

    def read_resource(self, uri: str) -> str:
        project_id = self.db.get_project_id(Path.cwd())
        
        if uri == "side://tips":
            import random
            tips = [

                "💡 Tip: Use 'side://monolith' to track your budget in real-time.",
                "💡 Tip: Badges like 'The Janitor' grant instant SU bounties.",
                "💡 Tip: If you run out of credits, the Manus Drip refills you tomorrow.",
                "💡 Tip: Keep .env files out of git to avoid Security findings.",
                "💡 Hack: Use 'strategy' tool with specific context for better ROI.",
            ]
            return random.choice(tips)

        if uri == "side://monolith":
            # Read from disk for speed/consistency
            monolith_path = Path.cwd() / ".side" / "MONOLITH.md"
            if monolith_path.exists():
                return monolith_path.read_text()
            return "# Monolith Not Found\nRun `side.welcome` to initialize."
            
        if uri == "side://activity":
            # Query DB
            with self.db._connection() as conn:
                rows = conn.execute(
                    """
                    SELECT tool, action, cost_tokens, created_at 
                    FROM activities 
                    WHERE project_id = ? 
                    ORDER BY created_at DESC LIMIT 20
                    """,
                    (project_id,)
                ).fetchall()
                data = [dict(row) for row in rows]
                return str(data) # JSON string

        if uri == "side://profile":
            # Query DB
            prof = self.db.get_profile(project_id)
            # Add Gamification stats
            with self.db._connection() as conn:
                stats = conn.execute("SELECT * FROM user_stats WHERE project_id = ?", (project_id,)).fetchone()
                if stats:
                    prof["gamification"] = dict(stats)
            return str(prof)

        raise ValueError(f"Unknown resource: {uri}")

resource_manager = ResourceManager()

@server.list_resources()
async def list_resources() -> list[Resource]:
    return resource_manager.list_resources()

@server.read_resource()
async def read_resource(uri: str) -> str:
    # Note: MCP read_resource returns content, usually list[TextContent] or similar in library wrapper,
    # but based on mcp-python sdk, the handler returns the content body or list of contents.
    # The standard signature for @server.read_resource() expects a return of `list[str | bytes | TextContent | ...]`?
    # Let's check mcp python sdk pattern. Usually it returns a list of contents.
    content = resource_manager.read_resource(uri)
    return [TextContent(type="text", text=content)]



@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """
    Handle tool calls with Extreme Fuzz-Resistance & Environment Isolation.
    """
    import time
    import traceback
    from side.services.billing import BillingService, SystemAction
    
    # [Extreme God Mode] Forensic 13: Subprocess Environment Isolation
    # Ensure sensitive keys are NEVER leaked to shell subprocesses spawned here.
    SENSITIVE_KEYS = ["GROQ_API_KEY", "SUPABASE_SERVICE_ROLE_KEY", "LEMONSQUEEZY_API_KEY"]
    for key in SENSITIVE_KEYS:
        os.environ.pop(key, None) # Remove from current process env before any potential shell spawn
    
    # [Extreme God Mode] Forensic 8: Fuzz-Resistance
    # Reject insane payloads immediately.
    MAX_ARG_SIZE = 1000000 # 1MB limit for arguments
    arg_str = str(arguments)
    if len(arg_str) > MAX_ARG_SIZE:
        return [TextContent(type="text", text=f"❌ **Fuzzing Detected**: Payload size {len(arg_str)} exceeds limit.")]

    start_time = time.time()
    logger.info(f"🔧 [GOD MODE EXECUTING] {name}")
    
    # [Billing] Calculate Cost
    TOOL_COST_MAP = {
        "architectural_decision": SystemAction.STRATEGY_CHAT,
        "strategic_review": SystemAction.SCAN_DEEP,
        "simulate": SystemAction.SCAN_DEEP,
        "audit_deep": SystemAction.SCAN_DEEP,
    }
    
    project_id = SimplifiedDatabase.get_project_id()
    billing = BillingService(SimplifiedDatabase()) # Lightweight init
    action = TOOL_COST_MAP.get(name)

    if action:
        # [Traffic Cop] Rate Limiting (Leaky Bucket)
        # Prevent runaway scripts from draining user balance in seconds.
        # Limit: 1 request per 2 seconds for expensive tools.
        # Implemented via simple time-check since last call.
        if not hasattr(server, "_last_action_time"):
            server._last_action_time = 0
            
        now = time.time()
        if now - server._last_action_time < 2.0:
            return [TextContent(type="text", text="⏳ **Traffic Cop**: Slow down! Strategic analysis takes time. (Rate Limit: 1 req/2s)")]
        
        server._last_action_time = now

        if not billing.can_afford(project_id, action):
             cost = billing.get_cost(action)
             balance = billing.db.get_token_balance(project_id)
             return [TextContent(type="text", text=f"❌ **Insufficient Strategic Units**: '{name}' costs {cost} SUs. You have {balance['balance']}. Upgrade to Pro for more.")]

    try:
        # Re-load env locally for internal logic ONLY if needed, 
        # but keep it out of the global process env to prevent shell leaks.
        if name == "purge_project":
            db = SimplifiedDatabase()
            success = db.purge_project_data(project_id, confirm=True) # Explicit confirm enforced
            result = f"🛡️ **Kill Switch Triggered**: Purged project `{project_id}`." if success else "❌ Purge failed."
        elif name == "audit_deep":
             # Execute global forensics tool
             query = arguments.get("query", "general audit")
             report = await _forensics_tool.scan_codebase(query)
             result = report
        else:
            result = await handle_tool_call(name, arguments or {})
        
        # [Memory] Intercept and Memorize (Fire-and-Forget)
        try:
             # Use the global interceptor initialized at module level
             # This avoids creating new clients on every request
             asyncio.create_task(_memory_interceptor.intercept(name, arguments, project_id, result))
        except Exception as mem_err:
             logger.warning(f"Memory Intercept Failed: {mem_err}")

        # [Billing] Charge if successful
        if action:
            new_balance = billing.charge(project_id, action, name, arguments)
            logger.info(f"💰 Charged {billing.get_cost(action)} SUs. New Balance: {new_balance}")

        elapsed = time.time() - start_time
        logger.info(f"✅ {name} SUCCESS ({elapsed:.3f}s)")
        
        # [The Live Wire]
        # Notify Client that Monolith and Activity Log have changed.
        # This forces the "App Window" to refresh instantly.
        try:
             # Broadcasting to all connected sessions (if supported) 
             # or current request context.
             # Note: Implementation depends on specific SDK version capabilities.
             # We assume a standard notification interface exists.
             if hasattr(server, "request_context"):
                 await server.request_context.session.send_resource_updated("side://monolith")
                 await server.request_context.session.send_resource_updated("side://activity")
                 await server.request_context.session.send_resource_updated("side://profile")
        except Exception:
            pass # Fail silently if notifications not supported yet

        return [TextContent(type="text", text=result)]
    except Exception as err:
        logger.error(f"❌ {name} ERROR: {str(err)}\n{traceback.format_exc()}")
        return [TextContent(type="text", text=f"Side Forensic Error: {str(err)}")]


async def run_server() -> None:
    """Run the Side MCP server with background services."""
    logger.info("🧠 Side starting up...")
    
    # Initialize background services
    # We use the current directory as the project root
    project_path = Path.cwd()
    service_manager = ServiceManager(project_path)
    
    try:
        # Start the Nervous System (File Watcher, Context Tracker, etc.)
        await service_manager.start()
        
        # [Memory] Schedule Nightly Maintenance (Async)
        # In a real app, this would be a proper cron. Here we just kick one off for demo/testing.
        # It's fire-and-forget.
        project_id = SimplifiedDatabase.get_project_id()
        asyncio.create_task(_memory_maintenance.run_nightly_consolidation(project_id))
        
        startup_time = time.time() - start_time
        logger.info("=" * 80)
        logger.info("🚀 Side SERVER IS LIVE")
        logger.info(f"⚡ Startup time: {startup_time:.3f}s")
        logger.info("💡 STRATEGIC TIP: Use 'strategy' tool with specific context for better ROI.")
        logger.info("=" * 80)
        
        async with stdio_server() as (read_stream, write_stream):
            # [Monolith] Evolution at Zero-Hour
            # Ensure the dashboard exists immediately upon connection.
            try:
                from side.storage.simple_db import SimplifiedDatabase
                from side.tools.planning import _generate_monolith_file
                db = SimplifiedDatabase()
                await _generate_monolith_file(db)
                logger.info("🏛️ Monolith Initialized.")
            except Exception as e:
                logger.warning(f"Initial Monolith generation failed: {e}")

            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        # Do not return 1, as the function signature is `-> None`
    finally:
        # Graceful shutdown of services
        logger.info("🛑 Shutting down nervous system...")
        await service_manager.stop()


def main() -> None:
    """Main entry point for side-mcp command."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Side shutting down...")
    except Exception as err:
        logger.error(f"sideMCP error: {err}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
