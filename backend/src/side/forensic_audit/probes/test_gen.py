"""
Test Gen Probe - Generative QA.
Automatically writes "Hostile" Unit Tests for complex functions to find edge cases.
"""

from typing import List
from pathlib import Path
import ast
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier

class TestGenProbe:
    """Forensic-level generative QA probe."""
    
    id = "forensic.test_gen"
    name = "Generative QA (Hostile Tests)"
    tier = Tier.DEEP
    dimension = "QA"
    
    async def run(self, context: ProbeContext) -> List[AuditResult]:
        if not context.llm_client or not context.llm_client.is_available():
            return [AuditResult(
                check_id="GEN-QA-000",
                check_name="Generative QA",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.INFO,
                notes="LLM Client not available"
            )]

        return [
            await self._generate_hostile_tests(context),
        ]

    async def _generate_hostile_tests(self, context: ProbeContext) -> AuditResult:
        """
        Identify complex functions and generate hostile tests.
        """
        complex_functions = []
        hostile_dir = Path(context.project_root) / "backend" / "tests" / "hostile"
        hostile_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Find candidates (Same logic as DeepLogicProbe - complexity > 5)
        for file_path in context.files:
            if not file_path.endswith('.py') or 'test' in file_path:
                continue
                
            try:
                content = Path(file_path).read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Simple complexity metric: lines of code
                        loc = node.end_lineno - node.lineno
                        if loc > 15: # Arbitrary threshold for demo
                            complex_functions.append((file_path, node.name, content))
            except Exception:
                continue
                
        if not complex_functions:
             return AuditResult(
                check_id="GEN-QA-001",
                check_name="Hostile Test Generation",
                dimension=self.dimension,
                status=AuditStatus.PASS,
                severity=Severity.INFO,
                notes="No complex functions found to test."
            )
            
        # Limit to top 1 candidate for safety/cost in demo
        complex_functions = complex_functions[:1]
        evidence = []
        
        for file_path, func_name, content in complex_functions:
            try:
                # We need to extract the function logic to prompt the LLM
                # (For now using full file content truncated is easier)
                
                test_filename = f"test_hostile_{func_name}.py"
                test_path = hostile_dir / test_filename
                
                if test_path.exists():
                     # Skip if already generated to avoid overwriting
                     continue
                
                prompt = f"""
                You are a QA Engineer specializing in "Hostile Testing".
                Write a pytest unit test for the function `{func_name}` in `{Path(file_path).name}`.
                
                GOAL: Break the code. 
                - Pass None
                - Pass empty strings
                - Pass huge numbers
                - Pass negative numbers
                
                CODE:
                ```python
                {content[:3000]}
                ```
                
                OUTPUT:
                Return ONLY the python code for the test file.
                imports: `from side.{Path(file_path).parent.name}.{Path(file_path).stem} import {func_name}` (adjust as needed).
                """
                
                response = context.llm_client.complete(
                    messages=[{"role": "user", "content": prompt}],
                    system_prompt="You are a hostile QA bot. Output code only.",
                    temperature=0.0
                )
                
                code_block = response
                if "```python" in response:
                    code_block = response.split("```python")[1].split("```")[0]
                elif "```" in response:
                    code_block = response.split("```")[1].split("```")[0]
                    
                test_path.write_text(code_block)
                
                evidence.append(AuditEvidence(
                    description=f"Generated Hostile Test for {func_name}",
                    file_path=str(test_path),
                    context=code_block[:200] + "...",
                    suggested_fix="Run `pytest backend/tests/hostile/`"
                ))
                    
            except Exception as e:
                print(f"Gen QA failed: {e}")
                continue

        return AuditResult(
            check_id="GEN-QA-001",
            check_name="Hostile Test Generation",
            dimension=self.dimension,
            status=AuditStatus.INFO if evidence else AuditStatus.PASS,
            severity=Severity.INFO, # Info only, we generated tests, didn't find bugs yet
            evidence=evidence,
            notes=f"Generated {len(evidence)} hostile tests.",
            recommendation="Run the generated tests to find runtime bugs."
        )
