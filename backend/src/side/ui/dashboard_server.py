import logging
import json
import sqlite3
from typing import List, Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sidelith God-View Dashboard")

# Paths
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
DB_PATH = Path("side_graph.sqlite")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/graph")
async def get_graph():
    """Returns the entire graph for visualization."""
    if not DB_PATH.exists():
        return {"nodes": [], "links": []}
        
    nodes = []
    links = []
    
    with sqlite3.connect(DB_PATH) as conn:
        # Fetch Objects
        cursor = conn.execute("SELECT uid, type, data, created_at FROM objects")
        rows = cursor.fetchall()
        for uid, type_name, data_json, created_at in rows:
            data = json.loads(data_json)
            nodes.append({
                "id": uid,
                "type": type_name,
                "label": data.get("name") or uid.split(":")[-1],
                "properties": data,
                "created_at": created_at
            })
            
        # Fetch Links
        cursor = conn.execute("SELECT source, target, type FROM links")
        rows = cursor.fetchall()
        for source, target, link_type in rows:
            links.append({
                "source": source,
                "target": target,
                "type": link_type
            })
            
    return {"nodes": nodes, "links": links}

@app.get("/api/stats")
async def get_stats():
    """Returns high-level forensic metrics."""
    with sqlite3.connect(DB_PATH) as conn:
        object_count = conn.execute("SELECT COUNT(*) FROM objects").fetchone()[0]
        link_count = conn.execute("SELECT COUNT(*) FROM links").fetchone()[0]
        type_counts = conn.execute("SELECT type, COUNT(*) FROM objects GROUP BY type").fetchall()
        
    return {
        "total_objects": object_count,
        "total_links": link_count,
        "by_type": {t: c for t, c in type_counts}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
