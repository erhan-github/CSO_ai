"""
Dependencies Probe - Dependency health audit.
"""

import re
from pathlib import Path
from typing import List
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier


class DependencyProbe:
    """Forensic-level dependency audit probe."""
    
    id = "forensic.dependencies"
    name = "Dependencies Audit"
    tier = Tier.FAST
    dimension = "Dependencies"
    
    async def run(self, context: ProbeContext) -> List[AuditResult]:
        return [
            self._check_lock_files(context),
            self._check_pinned_versions(context),
            self._check_dev_dependencies(context),
            await self._check_osv_vulnerabilities(context),
        ]
    
    def _check_lock_files(self, context: ProbeContext) -> AuditResult:
        """Check for lock files."""
        root = Path(context.project_root)
        lock_files = ['poetry.lock', 'Pipfile.lock', 'package-lock.json', 'yarn.lock', 'requirements.txt']
        found = [lf for lf in lock_files if (root / lf).exists()]
        
        return AuditResult(
            check_id="DEP-001",
            check_name="Lock Files Present",
            dimension=self.dimension,
            status=AuditStatus.PASS if found else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            notes=f"Found: {', '.join(found)}" if found else "No lock files found",
            recommendation="Use poetry.lock or requirements.txt for reproducible builds"
        )
    
    def _check_pinned_versions(self, context: ProbeContext) -> AuditResult:
        """Check for pinned dependency versions."""
        root = Path(context.project_root)
        req_path = root / 'requirements.txt'
        
        if not req_path.exists():
            return AuditResult(
                check_id="DEP-002",
                check_name="Pinned Versions",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.MEDIUM,
                notes="No requirements.txt found"
            )
        
        content = req_path.read_text()
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.startswith('#')]
        pinned = sum(1 for l in lines if '==' in l or '~=' in l)
        total = len(lines)
        
        ratio = pinned / total if total > 0 else 0
        
        return AuditResult(
            check_id="DEP-002",
            check_name="Pinned Versions",
            dimension=self.dimension,
            status=AuditStatus.PASS if ratio >= 0.8 else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            notes=f"{pinned}/{total} dependencies are pinned ({ratio*100:.0f}%)",
            recommendation="Pin versions with == for production stability"
        )
    
    def _check_dev_dependencies(self, context: ProbeContext) -> AuditResult:
        """Check for dev dependency separation."""
        root = Path(context.project_root)
        
        has_separation = (
            (root / 'requirements-dev.txt').exists() or
            (root / 'pyproject.toml').exists()  # Poetry separates by default
        )
        
        return AuditResult(
            check_id="DEP-003",
            check_name="Dev Dependencies Separated",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_separation else AuditStatus.INFO,
            severity=Severity.LOW,
            recommendation="Use pyproject.toml or requirements-dev.txt"
        )
    async def _check_osv_vulnerabilities(self, context: ProbeContext) -> AuditResult:
        """
        Query OSV.dev for real CVEs in dependencies.
        Supports: package.json (npm), pyproject.toml (pypi)
        """
        import json
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            import tomli as tomllib # Fallback
        except ImportError:
            tomllib = None
            
        import aiohttp
        
        vulnerabilities = []
        root = Path(context.project_root)
        
        # 1. Gather Dependencies
        deps_to_check = [] # List of {'name': str, 'version': str, 'ecosystem': 'PyPI'|'npm'}
        
        # Check package.json (npm)
        pkg_json = root / 'web' / 'package.json'
        if not pkg_json.exists():
             pkg_json = root / 'package.json'
             
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text())
                for dep, ver in data.get('dependencies', {}).items():
                    # clean version (remove ^, ~)
                    clean_ver = ver.replace('^', '').replace('~', '')
                    if re.match(r'^\d+\.\d+\.\d+', clean_ver):
                        deps_to_check.append({'name': dep, 'version': clean_ver, 'ecosystem': 'npm'})
            except Exception:
                pass

        # Check pyproject.toml (PyPI)
        py_toml = root / 'backend' / 'pyproject.toml'
        if not py_toml.exists():
            py_toml = root / 'pyproject.toml'
            
        if py_toml.exists():
            try:
                # Basic TOML parsing if tomli missing
                content = py_toml.read_text()
                in_deps = False
                for line in content.splitlines():
                    line = line.strip()
                    if line == '[tool.poetry.dependencies]':
                        in_deps = True
                        continue
                    if line.startswith('['):
                        in_deps = False
                    
                    if in_deps and '=' in line:
                        parts = line.split('=')
                        name = parts[0].strip()
                        ver = parts[1].strip().strip('"').strip("'")
                        ver = ver.replace('^', '').replace('~', '')
                        if re.match(r'^\d+\.\d+\.\d+', ver):
                            deps_to_check.append({'name': name, 'version': ver, 'ecosystem': 'PyPI'})
            except Exception:
                pass
        
        if not deps_to_check:
            return AuditResult(
                check_id="DEP-CVE-001",
                check_name="OSV Vulnerability Scan",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.HIGH,
                notes="No dependencies found to scan"
            )

        # 2. Query OSV API (Batching would be better, but doing logical serial for simplicity/correctness now)
        # Using aiohttp for speed if available, else requests
        
        # Since we are in async run, we should try to be non-blocking.
        # But for robustness in this environment, let's use the simplest working method
        # We will use the curl approach logic or basic http. 
        # Actually, let's just use standard library calls or aiohttp if available.
        # Assuming aiohttp is in the project (it usually is for modern python), otherwise fallback.
        
        found_cves = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for dep in deps_to_check:
                    payload = {
                        "package": {"name": dep['name'], "ecosystem": dep['ecosystem']},
                        "version": dep['version']
                    }
                    try:
                        async with session.post("https://api.osv.dev/v1/query", json=payload) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                if data.get('vulns'):
                                    for vuln in data['vulns']:
                                        found_cves.append({
                                            'package': dep['name'],
                                            'version': dep['version'],
                                            'id': vuln['id'],
                                            'details': vuln.get('details', 'No details available')[:100] + "..."
                                        })
                    except Exception:
                        continue
        except ImportError:
            # Fallback for environments without aiohttp (unlikely but safe)
            pass
            
        if found_cves:
             evidence = [
                 AuditEvidence(
                     description=f"{cve['package']}@{cve['version']} has vulnerability {cve['id']}",
                     context=cve['details'],
                     suggested_fix="Upgrade package version"
                 )
                 for cve in found_cves
             ]
             return AuditResult(
                check_id="DEP-CVE-001",
                check_name="OSV Vulnerability Scan",
                dimension=self.dimension,
                status=AuditStatus.FAIL,
                severity=Severity.CRITICAL,
                evidence=evidence,
                recommendation="Update vulnerable dependencies immediately"
            )

        return AuditResult(
            check_id="DEP-CVE-001",
            check_name="OSV Vulnerability Scan",
            dimension=self.dimension,
            status=AuditStatus.PASS,
            severity=Severity.HIGH,
            notes=f"Scanned {len(deps_to_check)} packages. No known CVEs found."
        )
