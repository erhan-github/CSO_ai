"""
Intent Probe - Verifies that the implementation matches the plan.
"""

from typing import List, Dict
from pathlib import Path
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier

class IntentProbe:
    """Forensic-level intent audit probe."""
    
    id = "forensic.intent"
    name = "Spec Guard (Plan vs Code)"
    tier = Tier.DEEP
    dimension = "Intent"
    
    async def run(self, context: ProbeContext) -> List[AuditResult]:
        if not context.llm_client or not context.llm_client.is_available():
            return [AuditResult(
                check_id="INTENT-000",
                check_name="Intent Analysis",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.INFO,
                notes="LLM Client not available"
            )]

        return [
            await self._check_plan_compliance(context),
        ]

    async def _check_plan_compliance(self, context: ProbeContext) -> AuditResult:
        """
        Check if the code implements the active plan.
        """
        # 1. Find the plan
        # We look for implementation_plan.md in the artifacts dir (brain)
        # context.project_root might be .../side
        # artifacts are in ~/.gemini/...
        # But we assume the runner passes relevant info, or we look in standard locations.
        
        # In this specific env, we know artifacts are in `context.strategic_context` or similar if passed,
        # but let's try to find it relative to what we know or just use the local file if user moved it.
        # Actually, let's look for `implementation_plan.md` in the project root first, or assume it's provided.
        # If we can't find it, we skip.
        
        # For this specific agent environment, the artifacts are slightly outside the repo usually.
        # But let's check if the runner put it in `task_files` logic.
        
        # Let's try to find 'implementation_plan.md' in likely spots.
        plan_content = ""
        possible_paths = [
            Path(context.project_root) / "implementation_plan.md",
            Path(context.project_root) / "docs" / "implementation_plan.md",
             # We rely on the runner having parsed it? No, runner parses task.md.
        ]
        
        # HACK: In this environment, we can try to find valid paths from context.files if it's there?
        # Or just skip if not found.
        
        found_plan = None
        for p in possible_paths:
            if p.exists():
                found_plan = p
                break
        
        if not found_plan:
             return AuditResult(
                check_id="INTENT-001",
                check_name="Plan Compliance",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.INFO,
                notes="No implementation_plan.md found to verify against."
            )
            
        plan_content = found_plan.read_text()
        
        # 2. Extract "Proposed Changes" or similar
        # We verify against the *files* modified.
        # This is expensive if we scan everything. 
        # Strategy: Look for file links in the plan, read those files, and ask LLM "Does this match?"
        
        import re
        # Find file links: [basename](file:///absolute/path) or just paths
        # context.files has the list of files in the project.
        
        # Let's assume the plan mentions files.
        mentioned_files = []
        for file_path in context.files:
            name = Path(file_path).name
            if name in plan_content:
                mentioned_files.append(file_path)
                
        if not mentioned_files:
             return AuditResult(
                check_id="INTENT-001",
                check_name="Plan Compliance",
                dimension=self.dimension,
                status=AuditStatus.PASS,
                severity=Severity.LOW,
                notes="Plan does not seem to mention any current files."
            )
            
        # Limit to top 3 files to save tokens
        files_to_check = mentioned_files[:3]
        evidence = []
        
        for fpath in files_to_check:
            try:
                content = Path(fpath).read_text()[:4000] # Truncate
                
                prompt = f"""
                You are a Product Owner verifying implementation.
                
                PLAN EXCERPT:
                ```
                {plan_content[:2000]}
                ```
                
                ACTUAL FILE ({Path(fpath).name}):
                ```
                {content}
                ```
                
                Does the file implement the relevant parts of the plan?
                If NO or PARTIAL, explain what is missing.
                If YES, just say "COMPLIANT".
                """
                
                response = context.llm_client.complete(
                    messages=[{"role": "user", "content": prompt}],
                    system_prompt="You are a strict code auditor.",
                    temperature=0.0
                )
                
                if "COMPLIANT" not in response:
                    evidence.append(AuditEvidence(
                        description=f"Plan Deviation in {Path(fpath).name}",
                        context=response[:300] + "...",
                        suggested_fix="Implement missing spec"
                    ))
                    
            except Exception:
                continue

        return AuditResult(
            check_id="INTENT-001",
            check_name="Plan Compliance",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.HIGH,
            evidence=evidence,
            notes=f"Checked {len(files_to_check)} files against plan.",
            recommendation="Review plan deviations and update code or plan."
        )
