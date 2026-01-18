# CSO.ai Monorepo

> **The Sidecar that thinks for you.**

This is the monorepo for CSO.ai, containing both the core intelligence engine and the web dashboard.

## Structure

- **`backend/`**: Python/MCP implementation of the Strategic Intelligence Engine.
- **`web/`**: Next.js Web Dashboard and API.

## Quick Start

### Backend (Python)
```bash
cd backend
uv pip install -e .
python -m cso_ai.server
```

### Frontend (Web)
```bash
cd web
npm install
npm run dev
```

## Contributing
See `backend/docs/CONTRIBUTING.md` for codebase standards.
