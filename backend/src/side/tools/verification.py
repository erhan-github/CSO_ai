
from typing import Any, Dict
from dataclasses import dataclass
from side.intel.forensic_engine import ForensicEngine

@dataclass
class ToolResult:
    content: str
    metadata: Dict[str, Any]

class VerificationTool:
    """
    Tool to verify if a specific finding has been fixed.
    """
    async def run(self, args: Dict[str, Any]) -> ToolResult:
        finding_type = args.get("finding_type")
        file_path = args.get("file_path")
        
        # 1. Run targeted scan
        engine = ForensicEngine(".")
        # bust cache
        from side.intel.forensic_engine import _FORENSIC_CACHE
        _FORENSIC_CACHE.clear()
        
        findings = await engine.scan()
        
        # 2. Check if the finding type still exists for the file
        matches = [f for f in findings if f.type == finding_type]
        if file_path:
            matches = [f for f in matches if f.file == file_path or f.file.endswith(file_path)]
            
        if not matches:
            return ToolResult(
                content=f"✅ VERIFICATION PASSED: No issues of type '{finding_type}' found in '{file_path or 'project'}'. Fix confirmed.",
                metadata={"status": "pass"}
            )
        else:
            return ToolResult(
                content=f"❌ VERIFICATION FAILED: Found {len(matches)} remaining issues of type '{finding_type}'.\nFirst failure: {matches[0].message}",
                metadata={"status": "fail", "remaining": len(matches)}
            )
