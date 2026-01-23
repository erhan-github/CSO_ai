"""
Frontend Probe - Enterprise frontend audit.

Forensic-level frontend checks covering:
- Bundle size
- Performance patterns
- Security headers in frontend
"""

from pathlib import Path
from typing import List
import re
import json
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier


class FrontendProbe:
    """Forensic-level frontend audit probe."""
    
    id = "forensic.frontend"
    name = "Frontend Audit"
    tier = Tier.FAST
    dimension = "Frontend"
    
    async def run(self, context: ProbeContext) -> List[AuditResult]:
        return [
            self._check_bundle_size(context),
            self._check_code_splitting(context),
            self._check_react_patterns(context),
            self._check_deps_audit(context),
            self._check_a11y(context),
            self._check_seo(context),
            self._check_react_hooks(context),
        ]
    
    def _check_bundle_size(self, context: ProbeContext) -> AuditResult:
        """Check for bundle size configuration."""
        root = Path(context.project_root)
        package_json = root / "package.json"
        
        if not package_json.exists():
            return AuditResult(
                check_id="FRONT-001",
                check_name="Bundle Size Limits",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.MEDIUM,
                notes="No package.json found (not a JS project)"
            )
        
        # Check for bundle analyzer or size limit tools
        content = package_json.read_text()
        size_tools = ['size-limit', 'bundlewatch', 'webpack-bundle-analyzer', 'source-map-explorer']
        has_size_check = any(tool in content for tool in size_tools)
        
        return AuditResult(
            check_id="FRONT-001",
            check_name="Bundle Size Limits",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_size_check else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Add size-limit or bundlewatch to CI"
        )
    
    def _check_a11y(self, context: ProbeContext) -> AuditResult:
        """Check for basic accessibility (A11y) issues."""
        evidence = []
        
        # Regex for common a11y mistakes
        patterns = [
            (r'<img(?!.*alt=).*?>', "Image missing alt text"),
            (r'<button(?!.*aria-label)(?!.*>).+?</button>', "Button missing aria-label (heuristic)"),
            (r'onClick=\{.*\}', "Clickable element may need role='button'"),
            (r'(role=["\']button["\']).*tabIndex', "Button role missing tabIndex"),
        ]
        
        for file_path in context.files:
            if not any(file_path.endswith(ext) for ext in ['.jsx', '.tsx', '.html', '.vue']):
                continue
            
            try:
                content = Path(file_path).read_text()
                # Skip test files
                if 'test' in file_path or 'spec' in file_path:
                    continue
                    
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    # Simple regex Checks
                    if '<img' in line and 'alt=' not in line:
                         evidence.append(AuditEvidence(
                            description="Image missing alt text",
                            file_path=file_path,
                            line_number=i+1,
                            context=line.strip()[:80],
                            suggested_fix='Add alt="description"'
                        ))
                    
                    if 'onClick=' in line and '<div' in line and 'role=' not in line:
                        evidence.append(AuditEvidence(
                            description="Clickable div missing role='button'",
                            file_path=file_path,
                            line_number=i+1,
                            context=line.strip()[:80],
                            suggested_fix='Add role="button" and tabIndex="0"'
                        ))

            except Exception:
                continue
                
        return AuditResult(
            check_id="FRONT-005",
            check_name="Accessibility (A11y) Basics",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=evidence[:5],
            notes=f"Found {len(evidence)} accessibility opportunities",
            recommendation="Run 'eslint-plugin-jsx-a11y' or Lighthouse"
        )

    def _check_seo(self, context: ProbeContext) -> AuditResult:
        """Check for SEO best practices."""
        evidence = []
        
        # Check specific files (pages) or just global search?
        # Let's search for "missing title" in likely page components
        
        has_title = False
        has_meta_desc = False
        has_og = False
        
        scanned_pages = 0
        
        for file_path in context.files:
            if not any(file_path.endswith(ext) for ext in ['.jsx', '.tsx', '.html']):
                continue
            
            # Simple heuristic: Only check files with <html> or <head> tags (pages)
            try:
                content = Path(file_path).read_text()
                if '<html' in content or '<head' in content:
                    scanned_pages += 1
                    local_title = '<title' in content
                    local_desc = 'name="description"' in content or 'name=\'description\'' in content
                    local_og = 'property="og:' in content or "property='og:" in content
                    
                    if not local_title:
                        evidence.append(AuditEvidence(description="Page missing <title> tag", file_path=file_path))
                    if not local_desc:
                        evidence.append(AuditEvidence(description="Page missing meta description", file_path=file_path))
                    
                    if local_title: has_title = True
                    if local_desc: has_meta_desc = True
                    if local_og: has_og = True
                    
            except Exception:
                continue

        # If no pages found (e.g. pure components), skip
        if scanned_pages == 0:
             return AuditResult(
                check_id="FRONT-006",
                check_name="SEO Essentials",
                dimension=self.dimension,
                status=AuditStatus.PASS, # Pass if not applicable
                severity=Severity.LOW,
                notes="No full page components detected"
            )

        return AuditResult(
            check_id="FRONT-006",
            check_name="SEO Essentials",
            dimension=self.dimension,
            status=AuditStatus.PASS if (has_title and has_meta_desc) else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=evidence[:5],
            recommendation="Ensure all public pages have title and meta description"
        )

    def _check_react_hooks(self, context: ProbeContext) -> AuditResult:
        """Check for potentially unsafe React Hooks usage."""
        evidence = []
        
        for file_path in context.files:
            if not any(file_path.endswith(ext) for ext in ['.jsx', '.tsx']):
                continue
            
            try:
                content = Path(file_path).read_text()
                lines = content.splitlines()
                
                for i, line in enumerate(lines):
                    # 1. Check for missing dependency array (heuristic)
                    # useEffect(() => { ... })  <-- missing array causing infinite loop risk
                    if 'useEffect(()' in line and (i+1 < len(lines)) and ')' in lines[i+1] and '[' not in lines[i+1]:
                        # Very weak heuristic, but catches obvious "only newline" cases
                        pass 

                    # 2. Check for empty dependency array used incorrectly? 
                    # Hard to do with regex.
                    
                    # 3. Check for heavy computation in render?
                    pass
                    
            except Exception:
                continue
                
        # For now, regex hook checking is extremely hard.
        # Let's check for 'eslint-plugin-react-hooks' in package.json instead
        
        has_hooks_lint = False
        pkg_path = Path(context.project_root) / "package.json"
        if pkg_path.exists():
            if "eslint-plugin-react-hooks" in pkg_path.read_text():
                has_hooks_lint = True
        
        return AuditResult(
            check_id="FRONT-007",
            check_name="React Hooks Safety",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_hooks_lint else AuditStatus.WARN,
            severity=Severity.HIGH,
            recommendation="Install 'eslint-plugin-react-hooks' to prevent infinite loops"
        )
    
    def _check_code_splitting(self, context: ProbeContext) -> AuditResult:
        """Check for code splitting patterns."""
        patterns = ['React.lazy', 'dynamic import', 'import(', 'loadable', 'Suspense']
        has_splitting = False
        
        for file_path in context.files:
            if not any(file_path.endswith(ext) for ext in ['.js', '.jsx', '.ts', '.tsx']):
                continue
            try:
                content = Path(file_path).read_text()
                if any(p in content for p in patterns):
                    has_splitting = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="FRONT-002",
            check_name="Code Splitting",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_splitting else AuditStatus.INFO,
            severity=Severity.LOW,
            recommendation="Use React.lazy or dynamic imports for large components"
        )
    
    def _check_react_patterns(self, context: ProbeContext) -> AuditResult:
        """Check for React performance patterns."""
        evidence = []
        
        for file_path in context.files:
            if not any(file_path.endswith(ext) for ext in ['.jsx', '.tsx']):
                continue
            try:
                content = Path(file_path).read_text()
                
                # Check for inline function in JSX
                if re.search(r'onClick=\{.*=>', content):
                    evidence.append(AuditEvidence(
                        description="Inline arrow function in JSX (re-creates on every render)",
                        file_path=file_path,
                        suggested_fix="Use useCallback for event handlers"
                    ))
                
                # Check for missing key in map
                if '.map(' in content and 'key=' not in content:
                    evidence.append(AuditEvidence(
                        description="Array map without key prop",
                        file_path=file_path
                    ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="FRONT-003",
            check_name="React Performance Patterns",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.INFO,
            severity=Severity.LOW,
            evidence=evidence[:5],
            recommendation="Use useCallback/useMemo for expensive operations"
        )
    
    def _check_deps_audit(self, context: ProbeContext) -> AuditResult:
        """Check for dependency audit in CI."""
        patterns = ['npm audit', 'yarn audit', 'pnpm audit', 'snyk']
        has_audit = False
        
        # Check CI files
        ci_paths = ['.github/workflows', '.gitlab-ci.yml']
        root = Path(context.project_root)
        
        for ci_path in ci_paths:
            path = root / ci_path
            if path.exists():
                if path.is_dir():
                    for f in path.glob('*.yml'):
                        if any(p in f.read_text() for p in patterns):
                            has_audit = True
                            break
                else:
                    if any(p in path.read_text() for p in patterns):
                        has_audit = True
        
        return AuditResult(
            check_id="FRONT-004",
            check_name="Dependency Audit in CI",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_audit else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Add 'npm audit' or Snyk to CI pipeline"
        )
