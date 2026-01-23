"""
Architecture Probe - The "Sentinel".
Enforces high-level design rules defined in .side/architecture_rules.md.
"""

from typing import List
from pathlib import Path
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier

class ArchitectureProbe:
    """Forensic-level architecture sentinel."""
    
    id = "forensic.architecture"
    name = "Architecture Sentinel"
    tier = Tier.DEEP
    dimension = "Architecture"
    
    async def run(self, context: ProbeContext) -> List[AuditResult]:
        if not context.llm_client or not context.llm_client.is_available():
            return [AuditResult(
                check_id="ARCH-000",
                check_name="Architecture Sentinel",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.INFO,
                notes="LLM Client not available"
            )]

        return [
            await self._check_architecture_rules(context),
        ]

    async def _check_architecture_rules(self, context: ProbeContext) -> AuditResult:
        """
        Scan code against .side/architecture_rules.md
        """
        root = Path(context.project_root)
        rules_file = root / ".side" / "architecture_rules.md"
        
        if not rules_file.exists():
             return AuditResult(
                check_id="ARCH-001",
                check_name="Rule Compliance",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.INFO,
                notes="No .side/architecture_rules.md found."
            )
            
        rules_content = rules_file.read_text()
        evidence = []
        
        # We can't check every file with LLM (too slow/expensive).
        # We need to be smart. 
        # 1. Filter relevant files based on rules?
        # 2. Or sample high-risk files?
        
        # Let's check "high risk" files: 
        # - Database files (sensitive)
        # - API routes (boundaries)
        # - Large files (complexity)
        
        candidates = []
        for fpath in context.files:
            p = Path(fpath)
            # High risk files logic
            if 'db' in p.name or 'storage' in p.name or 'api' in str(p):
                candidates.append(fpath)
            elif p.stat().st_size > 10000: # Large files > 10KB
                candidates.append(fpath)
                
        # Limit to top 20 for better coverage in demo
        candidates = candidates[:20]
        
        for fpath in candidates:
            try:
                content = Path(fpath).read_text()[:4000]
                
                prompt = f"""
                You are a Software Architect. Verify this code against our Architecture Rules.
                
                RULES:
                ```
                {rules_content}
                ```
                
                CODE ({Path(fpath).name}):
                ```
                {content}
                ```
                
                Does this code violate ANY rule?
                If YES, cite the rule # and explain.
                If NO, say "COMPLIANT".
                """
                
                response = context.llm_client.complete(
                    messages=[{"role": "user", "content": prompt}],
                    system_prompt="You are a strict sentinel. Zero tolerance.",
                    temperature=0.0
                )
                
                if "COMPLIANT" not in response:
                    evidence.append(AuditEvidence(
                        description=f"Architecture Violation in {Path(fpath).name}",
                        context=response[:300] + "...",
                        suggested_fix="Refactor to align with architecture_rules.md"
                    ))
                    
            except Exception:
                continue

        return AuditResult(
            check_id="ARCH-001",
            check_name="Rule Compliance",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.HIGH,
            evidence=evidence,
            notes=f"Checked {len(candidates)} high-risk files against Architecture Rules.",
            recommendation="Refactor violations immediately."
        )
