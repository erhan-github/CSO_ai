"""
Technical intelligence analyzer for CSO.ai.

Analyzes codebases to understand:
- Languages and frameworks
- Architecture patterns
- Code health
- Git activity
"""

import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TechnicalIntel:
    """Technical intelligence about a codebase."""

    languages: dict[str, int] = field(default_factory=dict)
    primary_language: str | None = None
    dependencies: dict[str, list[str]] = field(default_factory=dict)
    frameworks: list[str] = field(default_factory=list)
    architecture_patterns: list[str] = field(default_factory=list)
    health_signals: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "languages": self.languages,
            "primary_language": self.primary_language,
            "dependencies": self.dependencies,
            "frameworks": self.frameworks,
            "architecture_patterns": self.architecture_patterns,
            "health_signals": self.health_signals,
        }


@dataclass
class GitSignals:
    """Git repository signals."""

    is_git_repo: bool = False
    total_commits: int = 0
    recent_commits: int = 0  # Last 30 days
    contributors: list[str] = field(default_factory=list)
    active_branches: list[str] = field(default_factory=list)
    last_commit_date: str | None = None
    commit_frequency: str | None = None  # daily, weekly, monthly, sporadic
    recent_commit_messages: list[str] = field(default_factory=list)  # Last 10 commits
    recent_changed_files: list[str] = field(default_factory=list)  # Recently modified
    current_focus_areas: list[str] = field(default_factory=list)  # Inferred from commits

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_git_repo": self.is_git_repo,
            "total_commits": self.total_commits,
            "recent_commits": self.recent_commits,
            "contributors": self.contributors,
            "active_branches": self.active_branches,
            "last_commit_date": self.last_commit_date,
            "commit_frequency": self.commit_frequency,
            "recent_commit_messages": self.recent_commit_messages,
            "recent_changed_files": self.recent_changed_files,
            "current_focus_areas": self.current_focus_areas,
        }


@dataclass
class CodeIssues:
    """TODOs, FIXMEs, and other code issues."""

    todos: list[dict[str, str]] = field(default_factory=list)
    fixmes: list[dict[str, str]] = field(default_factory=list)
    hacks: list[dict[str, str]] = field(default_factory=list)
    total_issues: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "todos": self.todos[:10],  # Limit to 10
            "fixmes": self.fixmes[:10],
            "hacks": self.hacks[:10],
            "total_issues": self.total_issues,
        }


class TechnicalAnalyzer:
    """
    Analyzes technical aspects of a codebase.

    Provides deep understanding of:
    - Languages used and distribution
    - Frameworks and libraries
    - Architecture patterns
    - Code health signals
    - Git history
    - Code issues (TODOs, FIXMEs)
    """

    # Language detection by extension
    LANGUAGE_MAP: dict[str, str] = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".jsx": "JavaScript",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".java": "Java",
        ".go": "Go",
        ".rs": "Rust",
        ".rb": "Ruby",
        ".php": "PHP",
        ".cs": "C#",
        ".cpp": "C++",
        ".c": "C",
        ".m": "Objective-C",
        ".scala": "Scala",
        ".ex": "Elixir",
        ".exs": "Elixir",
        ".dart": "Dart",
        ".vue": "Vue",
        ".svelte": "Svelte",
    }

    # Framework detection from dependencies
    FRAMEWORK_PATTERNS: dict[str, list[str]] = {
        # Python
        "FastAPI": ["fastapi"],
        "Django": ["django"],
        "Flask": ["flask"],
        "Streamlit": ["streamlit"],
        "LangChain": ["langchain"],
        # JavaScript/TypeScript
        "React": ["react", "react-dom"],
        "Next.js": ["next"],
        "Vue": ["vue"],
        "Nuxt": ["nuxt"],
        "Angular": ["@angular/core"],
        "Svelte": ["svelte"],
        "Express": ["express"],
        "NestJS": ["@nestjs/core"],
        "Remix": ["@remix-run/react"],
        "Astro": ["astro"],
        # Mobile
        "React Native": ["react-native"],
        "Flutter": ["flutter"],
        "SwiftUI": ["SwiftUI"],
        "Expo": ["expo"],
        # Others
        "Tailwind CSS": ["tailwindcss"],
        "Prisma": ["@prisma/client"],
        "Drizzle": ["drizzle-orm"],
        "tRPC": ["@trpc/server"],
    }

    # Directories to skip
    SKIP_DIRS: set[str] = {
        "node_modules", ".git", "__pycache__", ".venv", "venv",
        "dist", "build", ".next", "target", ".idea", ".vscode",
        "Pods", ".build", "DerivedData", "vendor", ".cursor",
    }

    # File extensions to scan for TODOs
    CODE_EXTENSIONS: set[str] = {
        ".py", ".js", ".ts", ".tsx", ".jsx", ".swift", ".kt",
        ".java", ".go", ".rs", ".rb", ".php", ".cs", ".cpp",
        ".c", ".m", ".scala", ".ex", ".exs", ".dart", ".vue", ".svelte",
    }

    def __init__(self) -> None:
        """Initialize the analyzer."""
        pass

    async def analyze(self, path: str | Path) -> TechnicalIntel:
        """
        Perform full technical analysis on a codebase.

        Args:
            path: Root path of the codebase

        Returns:
            TechnicalIntel with all findings
        """
        root = Path(path).resolve()
        intel = TechnicalIntel()

        # Analyze different aspects
        intel.languages = await self._detect_languages(root)
        intel.primary_language = self._get_primary_language(intel.languages)
        intel.dependencies = await self._parse_dependencies(root)
        intel.frameworks = self._detect_frameworks(intel.dependencies)
        intel.architecture_patterns = await self._detect_architecture(root)
        intel.health_signals = await self._analyze_health(root)

        # Phase 3: Enhanced analysis
        git_signals = await self._analyze_git(root)
        intel.health_signals["git"] = git_signals.to_dict()

        code_issues = await self._extract_code_issues(root)
        intel.health_signals["code_issues"] = code_issues.to_dict()

        cursor_rules = await self._parse_cursor_rules(root)
        if cursor_rules:
            intel.health_signals["cursor_rules"] = cursor_rules

        return intel

    async def _detect_languages(self, root: Path) -> dict[str, int]:
        """Count files by programming language."""
        counts: dict[str, int] = {}

        for file_path in self._walk_files(root):
            ext = file_path.suffix.lower()
            if ext in self.LANGUAGE_MAP:
                lang = self.LANGUAGE_MAP[ext]
                counts[lang] = counts.get(lang, 0) + 1

        # Sort by count descending
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def _get_primary_language(self, languages: dict[str, int]) -> str | None:
        """Determine the primary language."""
        if not languages:
            return None
        return next(iter(languages))

    async def _parse_dependencies(self, root: Path) -> dict[str, list[str]]:
        """Parse all dependency files."""
        deps: dict[str, list[str]] = {}

        # package.json (npm)
        pkg_json = root / "package.json"
        if pkg_json.exists():
            deps["npm"] = self._parse_package_json(pkg_json)

        # requirements.txt (pip)
        req_txt = root / "requirements.txt"
        if req_txt.exists():
            deps["pip"] = self._parse_requirements_txt(req_txt)

        # pyproject.toml (Python)
        pyproject = root / "pyproject.toml"
        if pyproject.exists():
            deps["python"] = self._parse_pyproject_toml(pyproject)

        # Podfile (CocoaPods)
        podfile = root / "Podfile"
        if podfile.exists():
            deps["cocoapods"] = self._parse_podfile(podfile)

        # Package.swift (Swift PM)
        pkg_swift = root / "Package.swift"
        if pkg_swift.exists():
            deps["swift"] = self._parse_package_swift(pkg_swift)

        # go.mod
        go_mod = root / "go.mod"
        if go_mod.exists():
            deps["go"] = self._parse_go_mod(go_mod)

        # Cargo.toml
        cargo = root / "Cargo.toml"
        if cargo.exists():
            deps["cargo"] = self._parse_cargo_toml(cargo)

        return deps

    def _parse_package_json(self, path: Path) -> list[str]:
        """Parse package.json dependencies."""
        import json
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            deps = list(data.get("dependencies", {}).keys())
            deps.extend(data.get("devDependencies", {}).keys())
            return deps
        except (json.JSONDecodeError, OSError):
            return []

    def _parse_requirements_txt(self, path: Path) -> list[str]:
        """Parse requirements.txt."""
        try:
            content = path.read_text(encoding="utf-8")
            deps = []
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-"):
                    pkg = line.split("==")[0].split(">=")[0].split("<=")[0].split("[")[0]
                    deps.append(pkg.strip())
            return deps
        except OSError:
            return []

    def _parse_pyproject_toml(self, path: Path) -> list[str]:
        """Parse pyproject.toml dependencies."""
        try:
            content = path.read_text(encoding="utf-8")
            deps = []
            in_deps = False
            for line in content.splitlines():
                if "dependencies" in line and "=" in line:
                    in_deps = True
                    continue
                if in_deps:
                    if line.strip().startswith("]"):
                        in_deps = False
                    elif '"' in line:
                        match = re.search(r'"([^">=<\[]+)', line)
                        if match:
                            deps.append(match.group(1).strip())
            return deps
        except OSError:
            return []

    def _parse_podfile(self, path: Path) -> list[str]:
        """Parse Podfile dependencies."""
        try:
            content = path.read_text(encoding="utf-8")
            pods = re.findall(r"pod\s+['\"]([^'\"]+)['\"]", content)
            return pods
        except OSError:
            return []

    def _parse_package_swift(self, path: Path) -> list[str]:
        """Parse Package.swift dependencies."""
        try:
            content = path.read_text(encoding="utf-8")
            packages = re.findall(r'\.package\([^)]*url:\s*"([^"]+)"', content)
            names = []
            for url in packages:
                if "/" in url:
                    name = url.rstrip("/").split("/")[-1]
                    if name.endswith(".git"):
                        name = name[:-4]
                    names.append(name)
            return names
        except OSError:
            return []

    def _parse_go_mod(self, path: Path) -> list[str]:
        """Parse go.mod dependencies."""
        try:
            content = path.read_text(encoding="utf-8")
            deps = []
            in_require = False
            for line in content.splitlines():
                if line.strip().startswith("require"):
                    in_require = True
                    continue
                if in_require:
                    if line.strip() == ")":
                        in_require = False
                    else:
                        parts = line.strip().split()
                        if parts:
                            deps.append(parts[0])
            return deps
        except OSError:
            return []

    def _parse_cargo_toml(self, path: Path) -> list[str]:
        """Parse Cargo.toml dependencies."""
        try:
            content = path.read_text(encoding="utf-8")
            deps = []
            in_deps = False
            for line in content.splitlines():
                if "[dependencies]" in line or "[dev-dependencies]" in line:
                    in_deps = True
                    continue
                if in_deps:
                    if line.startswith("["):
                        in_deps = False
                    elif "=" in line:
                        pkg = line.split("=")[0].strip()
                        if pkg:
                            deps.append(pkg)
            return deps
        except OSError:
            return []

    def _detect_frameworks(self, dependencies: dict[str, list[str]]) -> list[str]:
        """Detect frameworks from dependencies."""
        all_deps = set()
        for deps in dependencies.values():
            all_deps.update(dep.lower() for dep in deps)

        detected = []
        for framework, patterns in self.FRAMEWORK_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in all_deps:
                    detected.append(framework)
                    break

        return detected

    async def _detect_architecture(self, root: Path) -> list[str]:
        """Detect architecture patterns."""
        patterns = []

        # Check for common patterns
        if (root / "src").is_dir():
            patterns.append("src-based structure")
        if (root / "app").is_dir():
            patterns.append("app directory")
        if (root / "api").is_dir() or (root / "src" / "api").is_dir():
            patterns.append("API layer")
        if (root / "components").is_dir() or (root / "src" / "components").is_dir():
            patterns.append("component-based")
        if (root / "tests").is_dir() or (root / "test").is_dir():
            patterns.append("tests present")
        if (root / "lib").is_dir() or (root / "libs").is_dir():
            patterns.append("library structure")
        if (root / "packages").is_dir():
            patterns.append("monorepo")
        if (root / "docker-compose.yml").exists() or (root / "docker-compose.yaml").exists():
            patterns.append("docker-compose")
        if (root / "Dockerfile").exists():
            patterns.append("dockerized")

        return patterns

    async def _analyze_health(self, root: Path) -> dict[str, Any]:
        """Analyze code health signals."""
        signals: dict[str, Any] = {}

        # Check for important files
        signals["has_readme"] = (root / "README.md").exists() or (root / "readme.md").exists()
        signals["has_gitignore"] = (root / ".gitignore").exists()
        signals["has_tests"] = (
            (root / "tests").is_dir() or
            (root / "test").is_dir() or
            (root / "__tests__").is_dir() or
            (root / "spec").is_dir()
        )
        signals["has_ci"] = (
            (root / ".github" / "workflows").is_dir() or
            (root / ".gitlab-ci.yml").exists() or
            (root / "Jenkinsfile").exists() or
            (root / ".circleci").is_dir()
        )
        signals["has_docker"] = (root / "Dockerfile").exists()
        signals["has_license"] = (root / "LICENSE").exists() or (root / "LICENSE.md").exists()

        return signals

    async def _analyze_git(self, root: Path) -> GitSignals:
        """Analyze git repository signals."""
        signals = GitSignals()
        git_dir = root / ".git"

        if not git_dir.exists():
            return signals

        signals.is_git_repo = True

        try:
            # Total commits
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                signals.total_commits = int(result.stdout.strip())

            # Recent commits (last 30 days)
            result = subprocess.run(
                ["git", "rev-list", "--count", "--since=30.days", "HEAD"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                signals.recent_commits = int(result.stdout.strip())

            # Contributors
            result = subprocess.run(
                ["git", "log", "--format=%aN", "--since=90.days"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                contributors = set(result.stdout.strip().split("\n"))
                signals.contributors = list(contributors)[:10]

            # Active branches
            result = subprocess.run(
                ["git", "branch", "-r", "--sort=-committerdate"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                branches = [b.strip() for b in result.stdout.strip().split("\n") if b.strip()]
                signals.active_branches = branches[:5]

            # Last commit date
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ci"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                signals.last_commit_date = result.stdout.strip()[:10]

            # Determine commit frequency
            if signals.recent_commits >= 20:
                signals.commit_frequency = "daily"
            elif signals.recent_commits >= 5:
                signals.commit_frequency = "weekly"
            elif signals.recent_commits >= 1:
                signals.commit_frequency = "monthly"
            else:
                signals.commit_frequency = "sporadic"

            # Get recent commit messages (last 10)
            result = subprocess.run(
                ["git", "log", "--oneline", "-10", "--format=%s"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                messages = [m.strip() for m in result.stdout.strip().split("\n") if m.strip()]
                signals.recent_commit_messages = messages[:10]

            # Get recently changed files (last 7 days)
            result = subprocess.run(
                ["git", "log", "--name-only", "--since=7.days", "--format="],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                files = set(f.strip() for f in result.stdout.strip().split("\n") if f.strip())
                signals.recent_changed_files = list(files)[:20]

            # Infer current focus areas from commit messages
            signals.current_focus_areas = self._infer_focus_areas(
                signals.recent_commit_messages,
                signals.recent_changed_files,
            )

        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass

        return signals

    def _infer_focus_areas(
        self,
        commit_messages: list[str],
        changed_files: list[str],
    ) -> list[str]:
        """Infer what the developer is currently working on from git activity."""
        focus_areas: set[str] = set()

        # Keywords to detect in commit messages
        focus_keywords = {
            "auth": ["auth", "login", "logout", "session", "jwt", "oauth", "password"],
            "api": ["api", "endpoint", "route", "rest", "graphql", "request", "response"],
            "database": ["database", "db", "migration", "schema", "query", "sql", "model"],
            "ui": ["ui", "frontend", "component", "css", "style", "layout", "design"],
            "testing": ["test", "spec", "mock", "fixture", "coverage", "pytest", "jest"],
            "docs": ["doc", "readme", "comment", "documentation"],
            "security": ["security", "vulnerability", "auth", "encrypt", "sanitize"],
            "performance": ["performance", "optimize", "cache", "speed", "slow", "fast"],
            "deployment": ["deploy", "docker", "ci", "cd", "pipeline", "build", "release"],
            "refactor": ["refactor", "cleanup", "reorganize", "restructure", "simplify"],
            "bug": ["fix", "bug", "issue", "error", "crash", "broken"],
            "feature": ["add", "new", "feature", "implement", "create"],
            "config": ["config", "env", "setting", "option", "parameter"],
            "integration": ["integrate", "webhook", "api", "stripe", "supabase", "third-party"],
        }

        # Check commit messages
        all_text = " ".join(commit_messages).lower()
        for area, keywords in focus_keywords.items():
            if any(kw in all_text for kw in keywords):
                focus_areas.add(area)

        # Check file paths for additional signals
        all_paths = " ".join(changed_files).lower()
        path_signals = {
            "auth": ["auth", "login", "session"],
            "api": ["api", "routes", "endpoints", "handlers"],
            "database": ["models", "migrations", "schema", "db"],
            "ui": ["components", "views", "pages", "styles", "css"],
            "testing": ["test", "spec", "__tests__"],
            "docs": ["docs", "readme"],
            "config": ["config", ".env", "settings"],
        }

        for area, patterns in path_signals.items():
            if any(p in all_paths for p in patterns):
                focus_areas.add(area)

        return list(focus_areas)[:5]  # Return top 5 focus areas

    async def _extract_code_issues(self, root: Path) -> CodeIssues:
        """Extract TODOs, FIXMEs, and HACKs from code."""
        issues = CodeIssues()

        todo_pattern = re.compile(r"#\s*TODO[:\s]*(.*)|//\s*TODO[:\s]*(.*)", re.IGNORECASE)
        fixme_pattern = re.compile(r"#\s*FIXME[:\s]*(.*)|//\s*FIXME[:\s]*(.*)", re.IGNORECASE)
        hack_pattern = re.compile(r"#\s*HACK[:\s]*(.*)|//\s*HACK[:\s]*(.*)", re.IGNORECASE)

        for file_path in self._walk_files(root):
            if file_path.suffix.lower() not in self.CODE_EXTENSIONS:
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                rel_path = str(file_path.relative_to(root))

                for line_num, line in enumerate(content.splitlines(), 1):
                    # TODOs
                    match = todo_pattern.search(line)
                    if match:
                        text = match.group(1) or match.group(2) or ""
                        issues.todos.append({
                            "file": rel_path,
                            "line": line_num,
                            "text": text.strip()[:100],
                        })

                    # FIXMEs
                    match = fixme_pattern.search(line)
                    if match:
                        text = match.group(1) or match.group(2) or ""
                        issues.fixmes.append({
                            "file": rel_path,
                            "line": line_num,
                            "text": text.strip()[:100],
                        })

                    # HACKs
                    match = hack_pattern.search(line)
                    if match:
                        text = match.group(1) or match.group(2) or ""
                        issues.hacks.append({
                            "file": rel_path,
                            "line": line_num,
                            "text": text.strip()[:100],
                        })

            except (OSError, UnicodeDecodeError):
                continue

        issues.total_issues = len(issues.todos) + len(issues.fixmes) + len(issues.hacks)
        return issues

    async def _parse_cursor_rules(self, root: Path) -> dict[str, Any] | None:
        """Parse .cursorrules or cursor rules file."""
        rules_paths = [
            root / ".cursorrules",
            root / ".cursor" / "rules",
        ]

        for path in rules_paths:
            if path.exists():
                try:
                    content = path.read_text(encoding="utf-8")

                    # Extract key themes from rules
                    themes = []
                    content_lower = content.lower()

                    if "security" in content_lower:
                        themes.append("Security-focused")
                    if "type" in content_lower and ("strict" in content_lower or "safe" in content_lower):
                        themes.append("Type Safety")
                    if "test" in content_lower:
                        themes.append("Testing")
                    if "performance" in content_lower:
                        themes.append("Performance")
                    if "error" in content_lower and "handl" in content_lower:
                        themes.append("Error Handling")
                    if "document" in content_lower or "docstring" in content_lower:
                        themes.append("Documentation")
                    if "clean" in content_lower or "refactor" in content_lower:
                        themes.append("Code Quality")

                    return {
                        "path": str(path.relative_to(root)),
                        "themes": themes,
                        "length": len(content),
                    }
                except (OSError, UnicodeDecodeError):
                    continue

        return None

    def _walk_files(self, root: Path) -> list[Path]:
        """Walk files, skipping ignored directories."""
        files = []

        def should_skip(path: Path) -> bool:
            return any(part in self.SKIP_DIRS for part in path.parts)

        for path in root.rglob("*"):
            if path.is_file() and not should_skip(path):
                files.append(path)

        return files
