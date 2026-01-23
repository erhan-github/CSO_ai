"""
LLM Quality Probe - AI/LLM integration audit.
"""

import re
from pathlib import Path
from typing import List
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier


class LLMQualityProbe:
    """Forensic-level LLM quality audit probe."""
    
    id = "forensic.llm_quality"
    name = "LLM Quality Audit"
    tier = Tier.FAST
    dimension = "AI/LLM Quality"
    
    async def run(self, context: ProbeContext) -> List[AuditResult]:
        return [
            self._check_token_limits(context),
            self._check_fallbacks(context),
            self._check_output_validation(context),
            self._check_prompt_injection(context),
            self._check_rate_limiting(context),
            self._check_cost_tracking(context),
            self._check_system_prompt(context),
            self._check_temperature_safety(context),
        ]
    
    def _check_token_limits(self, context: ProbeContext) -> AuditResult:
        """Check for token limit configuration."""
        patterns = ['max_tokens', 'token_limit', 'max_output_tokens']
        found_count = 0
        
        for file_path in context.files:
            if not any(file_path.endswith(ext) for ext in ['.py', '.ts', '.js', '.tsx', '.jsx']):
                continue
            try:
                content = Path(file_path).read_text()
                for p in patterns:
                    found_count += content.count(p)
            except Exception:
                continue
        
        return AuditResult(
            check_id="LLM-001",
            check_name="Token Limits Configured",
            dimension=self.dimension,
            status=AuditStatus.PASS if found_count > 0 else AuditStatus.WARN,
            severity=Severity.HIGH,
            notes=f"Found {found_count} token limit configurations",
            recommendation="Set max_tokens on all LLM calls"
        )
    
    def _check_fallbacks(self, context: ProbeContext) -> AuditResult:
        """Check for fallback strategies."""
        patterns = ['fallback', 'backup_model', 'template_', 'default_response']
        has_fallback = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content.lower() for p in patterns):
                    has_fallback = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="LLM-002",
            check_name="Fallback Strategies",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_fallback else AuditStatus.WARN,
            severity=Severity.HIGH,
            recommendation="Add fallback responses when LLM fails"
        )
    
    def _check_output_validation(self, context: ProbeContext) -> AuditResult:
        """Check for LLM output validation."""
        patterns = ['validate_', 'QualityControl', 'verify_output', 'is_valid']
        has_validation = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content for p in patterns):
                    has_validation = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="LLM-003",
            check_name="Output Validation",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_validation else AuditStatus.WARN,
            severity=Severity.HIGH,
            recommendation="Validate LLM outputs before using"
        )
    
    def _check_prompt_injection(self, context: ProbeContext) -> AuditResult:
        """Check for prompt injection prevention."""
        evidence = []
        patterns = [
            (r'f["\'].*\{user_input\}', "User input in f-string prompt"),
            (r'\.format\(.*user', "User input via .format() in prompt"),
        ]
        
        for file_path in context.files:
            if not any(file_path.endswith(ext) for ext in ['.py', '.ts', '.js', '.tsx', '.jsx']):
                continue
            try:
                content = Path(file_path).read_text()
                for pattern, desc in patterns:
                    if re.search(pattern, content):
                        evidence.append(AuditEvidence(
                            description=desc,
                            file_path=file_path
                        ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="LLM-004",
            check_name="Prompt Injection Prevention",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.HIGH,
            evidence=evidence[:5],
            recommendation="Sanitize user inputs before including in prompts"
        )
    
    def _check_rate_limiting(self, context: ProbeContext) -> AuditResult:
        """Check for LLM rate limiting."""
        patterns = ['rate_limit', 'RateLimiter', 'throttle', 'limiter']
        has_limiting = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content for p in patterns):
                    has_limiting = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="LLM-005",
            check_name="LLM Rate Limiting",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_limiting else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Add rate limiting to prevent abuse"
        )
    
    def _check_cost_tracking(self, context: ProbeContext) -> AuditResult:
        """Check for LLM cost tracking."""
        patterns = ['cost_tokens', 'token_cost', 'log_activity', 'usage_']
        has_tracking = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content for p in patterns):
                    has_tracking = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="LLM-006",
            check_name="LLM Cost Tracking",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_tracking else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Track token usage per call for cost monitoring"
        )

    def _check_system_prompt(self, context: ProbeContext) -> AuditResult:
        """Check if LLM calls include a System Prompt (Best Practice)."""
        evidence = []
        
        # Regex to find message construction without 'system' role
        # Heuristic: Find specific list definitions messages=[...]
        # This is hard with regex, maybe better with AST?
        # Let's try simple regex: If a file imports openai/llm but doesn't mention "role": "system" or "role": 'system'
        
        for file_path in context.files:
            if not any(file_path.endswith(ext) for ext in ['.py', '.ts', '.js', '.tsx', '.jsx']):
                continue
                
            try:
                content = Path(file_path).read_text()
                
                # Check if it looks like an LLM file
                if not any(k in content for k in ['openai', 'anthropic', 'LLMClient', 'chat.completions']):
                    continue
                
                # Check if system role is mentioned
                has_system = 'role": "system"' in content or "role': 'system'" in content or 'role": "system"' in content
                
                if not has_system:
                     evidence.append(AuditEvidence(
                        description="LLM code detected but no System Prompt found",
                        file_path=file_path,
                        suggested_fix="Always include {'role': 'system', ...} to ground the model"
                    ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="LLM-007",
            check_name="System Prompt Enforcement",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=evidence[:5],
            recommendation="Always use System Prompts to define agent behavior"
        )

    def _check_temperature_safety(self, context: ProbeContext) -> AuditResult:
        """Check for potentially unsafe temperature settings."""
        evidence = []
        
        # Regex to find high temperature usage
        # temperature=0.9 or temperature = 0.9
        high_temp_pattern = r'temperature\s*=\s*(0\.[7-9]|1\.0|1|2)'
        
        for file_path in context.files:
            if not any(file_path.endswith(ext) for ext in ['.py', '.ts', '.js', '.tsx', '.jsx']):
                continue
                
            try:
                content = Path(file_path).read_text()
                
                for line_idx, line in enumerate(content.splitlines(), 1):
                    match = re.search(high_temp_pattern, line)
                    if match:
                        # Context: Is this code generation? 
                        # Simple heuristic: Just warn on high temp generally for now as a "Check this"
                        evidence.append(AuditEvidence(
                            description=f"High temperature detected ({match.group(1)})",
                            file_path=file_path,
                            line_number=line_idx,
                            suggested_fix="Use temp < 0.7 for deterministic tasks (coding), > 0.7 for creative"
                        ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="LLM-008",
            check_name="LLM Parameter Safety",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.INFO,
            severity=Severity.LOW,
            evidence=evidence[:5],
            recommendation="Verify temperature settings match the use case (Code=Low, Creative=High)"
        )
