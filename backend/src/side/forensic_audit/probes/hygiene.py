from typing import List
from pathlib import Path
from ..core import AuditResult, AuditStatus, ProbeContext, Severity, AuditFixRisk

class HygieneProbe:
    """
    Checks for project hygiene and cleanliness.
    
    Detects:
    - Root directory clutter
    - Misplaced scripts (should be in scripts/ or src/)
    - Outdated temporary documentation (TODO.md, etc.)
    - Empty or temporary directories
    """
    
    id = "forensic.hygiene"
    name = "Hygiene Audit"
    dimension = "Hygiene"

    async def run(self, context: ProbeContext) -> List[AuditResult]:
        results = []
        root = Path(context.project_root)
        
        # 1. Root Clutter Check
        results.extend(self._check_root_clutter(root))
        
        # 2. Misplaced Scripts Check
        results.extend(self._check_misplaced_scripts(root))
        
        # 3. Outdated Docs Check
        results.extend(self._check_outdated_docs(root, context.files))
        
        return results
        
    def _check_root_clutter(self, root: Path) -> List[AuditResult]:
        """Warn if root directory has too many files."""
        results = []
        
        # Count non-hidden files in root
        try:
            root_files = [f for f in root.iterdir() if f.is_file() and not f.name.startswith('.')]
        except Exception:
            return []
            
        threshold = 15
        
        if len(root_files) > threshold:
            results.append(AuditResult(
                check_id="HYG-001",
                check_name="Root Directory Clutter",
                status=AuditStatus.WARN,
                severity=Severity.LOW,
                dimension=self.dimension,
                notes=f"Root directory contains {len(root_files)} visible files (threshold: {threshold}).",
                recommendation="Move configuration files to a `config/` folder or scripts to `scripts/`.",
                fix_risk=AuditFixRisk.SAFE
            ))
        else:
            results.append(AuditResult(
                check_id="HYG-001",
                check_name="Root Directory Clutter",
                status=AuditStatus.PASS,
                severity=Severity.LOW,
                dimension=self.dimension,
                notes=f"Root directory is clean ({len(root_files)} files).",
            ))
            
        return results

    def _check_misplaced_scripts(self, root: Path) -> List[AuditResult]:
        """Check for script files in root that should be organized."""
        results = []
        
        # Extensions to watch for in root
        script_exts = {'.py', '.sh', '.js', '.ts', '.go', '.rb'}
        
        # Allowed root scripts (standard configs/entrypoints)
        allowed = {
            'setup.py', 'conftest.py', 'manage.py', # Python
            'vite.config.ts', 'jest.config.js', 'next.config.js', 'tailwind.config.js', # JS/TS
            'hardhat.config.js'
        }
        
        misplaced = []
        try:
            for f in root.iterdir():
                if f.is_file() and not f.name.startswith('.') and f.suffix in script_exts:
                    if f.name not in allowed and not f.name.endswith('.config.js') and not f.name.endswith('rc.js'):
                        misplaced.append(f.name)
        except Exception:
            pass
            
        if misplaced:
            results.append(AuditResult(
                check_id="HYG-002",
                check_name="Misplaced Root Scripts",
                status=AuditStatus.WARN,
                severity=Severity.MEDIUM,
                dimension=self.dimension,
                notes=f"Found {len(misplaced)} script(s) in root that may need organization: {', '.join(misplaced[:3])}...",
                recommendation="Move utility scripts to a `scripts/` directory.",
                fix_risk=AuditFixRisk.SAFE
            ))
        else:
            results.append(AuditResult(
                check_id="HYG-002",
                check_name="Misplaced Root Scripts",
                status=AuditStatus.PASS,
                severity=Severity.MEDIUM,
                dimension=self.dimension,
                notes="No misplaced scripts found in root.",
            ))
            
        return results

    def _check_outdated_docs(self, root: Path, all_files: List[str]) -> List[AuditResult]:
        """Check for temporary or outdated documentation files."""
        results = []
        
        # Patterns to flag (case insensitive)
        # Patterns to flag (case insensitive)
        flag_patterns = {
            'todo.md', 'temp.md', 'scratches.md', 'notes.md', 'draft.md', 
            'high_issues.txt', 'audit_dump.txt', 'temp.log', 'debug.log'
        }
        
        # Glob patterns for temporary check files
        glob_patterns = ['check_*.txt', 'test_*.log', '*.tmp']
        
        found_docs = []
        for file_path in all_files:
            path = Path(file_path)
            
            # Check exact match or known temp names
            if path.name.lower() in flag_patterns:
                try:
                    rel_path = path.relative_to(root)
                    found_docs.append(str(rel_path))
                except ValueError:
                    found_docs.append(path.name)
                continue
                
            # Check glob patterns
            import fnmatch
            for pat in glob_patterns:
                if fnmatch.fnmatch(path.name, pat):
                    try:
                        rel_path = path.relative_to(root)
                        found_docs.append(str(rel_path))
                    except ValueError:
                        found_docs.append(path.name)
                    break

        if found_docs:
            results.append(AuditResult(
                check_id="HYG-003",
                check_name="Temporary & Junk Files",
                status=AuditStatus.WARN,
                severity=Severity.LOW,
                dimension=self.dimension,
                notes=f"Found {len(found_docs)} temporary files: {', '.join(found_docs[:5])}...",
                recommendation="Clean up temporary check files and logs.",
                fix_risk=AuditFixRisk.SAFE
            ))
        else:
            results.append(AuditResult(
                check_id="HYG-003",
                check_name="Temporary Documentation",
                status=AuditStatus.PASS,
                severity=Severity.LOW,
                dimension=self.dimension,
                notes="No temporary documentation files found.",
            ))
            
        return results
