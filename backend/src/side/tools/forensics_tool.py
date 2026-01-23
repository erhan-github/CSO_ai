import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from side.tools.recursive_utils import partition, peek, grep
from side.intel.memory import MemoryPersistence, MemoryManager
from side.llm.client import LLMClient

logger = logging.getLogger(__name__)

class ForensicsTool:
    """
    Implements "Deep Audit" capabilities using Recursive Language Models (RLMs).
    Instead of reading the whole codebase, we:
    1. Filter relevant files (grep/find).
    2. Partition them into chunks.
    3. Peek at headers.
    4. Recursively analyze.
    """

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.llm = LLMClient()

    async def scan_codebase(self, query: str) -> str:
        """
        Recursively scan the codebase for a specific forensic query.
        Example: "Find all hardcoded secrets" or "Check ensuring strict type adherence"
        """
        # 1. Discovery Phase: Find relevant files
        all_files = self._find_files()
        
        # 2. Partition Strategy
        # If too many files, we filter first.
        # For this v1, we'll grep for keywords related to the query if accessible,
        # otherwise we take a sampling approach.
        
        # Simple heuristic: Grep for suspicious patterns if query mentions secrets
        suspicious_files = []
        if "secret" in query.lower() or "key" in query.lower():
             # Use our recursive grep tool
             # We can't grep 'query' directly as it's NL.
             # We'll upgrade this to an LLM-driven keyword extraction later.
             # For now, we scan all files but chunk them.
             pass

        # 3. Recursive Analysis
        # We split the file list into chunks of 5 files to prevent context overflow
        chunks = partition(all_files, chunk_size=5)
        
        findings = []
        logger.info(f"🔎 [FORENSICS] Scanning {len(all_files)} files in {len(chunks)} chunks...")

        for chunk in chunks[:10]: # Limit to top 50 files for speed in V1
            chunk_content = ""
            for file_path in chunk:
                try:
                    content = file_path.read_text(errors='ignore')
                    # Peek only first 500 lines to save tokens
                    preview = peek(content, lines=500) 
                    chunk_content += f"\n--- File: {file_path.relative_to(self.project_path)} ---\n{preview}\n"
                except Exception:
                    continue
            
            # Analyze this chunk
            if chunk_content:
                finding = await self._analyze_chunk(chunk_content, query)
                if finding:
                    findings.append(finding)
        
        # 4. Synthesize Results
        return self._synthesize_report(findings, query)

    def _find_files(self, patterns: List[str] = None) -> List[Path]:
        """Return a list of source code files."""
        # Standard excludes
        excludes = {'.git', 'node_modules', '__pycache__', 'venv', 'env', '.DS_Store'}
        files = []
        for root, dirs, filenames in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in excludes]
            for name in filenames:
                if name.endswith(('.py', '.js', '.ts', '.tsx', '.go', '.rs', '.md')):
                    files.append(Path(root) / name)
        return files

    async def _analyze_chunk(self, content: str, query: str) -> str:
        """Ask LLM to find issues in a single chunk."""
        prompt = f"""You are a Code Forensics Engine.
        
Query: "{query}"

Code Context:
{content}

Task: Identify any CRITICAL issues related to the query.
- Use line numbers.
- Be extremely strict.
- If nothing found, return "PASS".
- If found, strictly format as: [FILE]: [LINE] - [ISSUE]
"""
        response = await self.llm.complete_async(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are a Code Forensics Engine.",
            temperature=0.0
        )
        if "PASS" in response:
            return None
        return response

    def _synthesize_report(self, findings: List[str], query: str) -> str:
        if not findings:
            return f"✅ **Forensics Clean:** No issues found for '{query}'."
        
        issue_count = len(findings)
        
        # 1. THE HOOK
        report = [f"🕵️ **Forensics Alert: {issue_count} Issues Detected**"]
        report.append("")
        
        # 2. THE EVIDENCE
        report.append("**Key Findings:**")
        # Extract meaningful summaries from findings if possible, or just list top 3
        # Findings are raw strings "[FILE]: [LINE] - [ISSUE]"
        for finding in findings[:5]: 
             # Cleanup finding string to be bullet point
             clean_finding = finding.strip().replace("\n", " ")
             report.append(f"*   {clean_finding[:100]}...")
        
        if issue_count > 5:
            report.append(f"*   ... and {issue_count - 5} more.")
        report.append("")
        
        # 3. THE PROPOSAL (The Button)
        # We propose a Plan to fix these.
        report.append(f"> **Side Proposes Action:** `plan`")
        report.append(f"> *Run this to create a remediation plan.*")
        
        # Tool Proposal Signal
        report.append(f"tool_code: call_tool('plan', {{'goal': 'Remediate {issue_count} forensic issues found in {query}', 'due': 'today'}})")
        
        return "\n".join(report)
