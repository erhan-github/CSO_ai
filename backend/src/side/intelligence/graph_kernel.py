import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set
import json
from .scrubber import SovereignScrubber
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class GraphObject:
    """A Palantir-style object in the Sidelith Data Fabric."""
    uid: str
    type: str  # 'symbol', 'intent', 'decision', 'outcome', 'commit'
    properties: Dict[str, Any] = field(default_factory=dict)
    links: Set[tuple[str, str]] = field(default_factory=set) # (neighbor_uid, link_type)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def add_link(self, neighbor_uid: str, link_type: str):
        self.links.add((neighbor_uid, link_type))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uid": self.uid,
            "type": self.type,
            "properties": self.properties,
            "links": list(self.links),
            "created_at": self.created_at
        }

class GraphKernel:
    """
    The Central Reasoning Engine.
    Unifies all silos into a single 'Engineering Data Fabric'.
    Powered by SQLite for Palantir-level durability.
    """
    def __init__(self, storage_path: str = "side_graph.sqlite"):
        self.storage_path = storage_path
        self.objects: Dict[str, GraphObject] = {}
        self.scrubber = SovereignScrubber()
        self._init_db()
        self._load()

    def _init_db(self):
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS objects (
                    uid TEXT PRIMARY KEY,
                    type TEXT,
                    data TEXT,
                    created_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS links (
                    source TEXT,
                    target TEXT,
                    type TEXT,
                    PRIMARY KEY (source, target, type)
                )
            """)
            conn.commit()

    def upsert_object(self, obj: GraphObject):
        # 🛡️ SOVEREIGN MANDATE: Every ingestion must be scrubbed.
        obj.properties = self.scrubber.validate_ingestion(obj.uid, obj.type, obj.properties)
        
        if obj.uid in self.objects:
            self.objects[obj.uid].properties.update(obj.properties)
            self.objects[obj.uid].links.update(obj.links)
        else:
            self.objects[obj.uid] = obj
        
        # Persist to SQLite
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO objects (uid, type, data, created_at) VALUES (?, ?, ?, ?)",
                (obj.uid, obj.type, json.dumps(obj.properties), obj.created_at)
            )
            for target, link_type in obj.links:
                conn.execute(
                    "INSERT OR IGNORE INTO links (source, target, type) VALUES (?, ?, ?)",
                    (obj.uid, target, link_type)
                )
            conn.commit()

    def link(self, source_uid: str, target_uid: str, link_type: str, bidirectional: bool = True):
        if source_uid in self.objects and target_uid in self.objects:
            self.objects[source_uid].add_link(target_uid, link_type)
            if bidirectional:
                self.objects[target_uid].add_link(source_uid, f"inverse_{link_type}")
            
            # Persist links
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute("INSERT OR IGNORE INTO links (source, target, type) VALUES (?, ?, ?)",
                             (source_uid, target_uid, link_type))
                if bidirectional:
                    conn.execute("INSERT OR IGNORE INTO links (source, target, type) VALUES (?, ?, ?)",
                                 (target_uid, source_uid, f"inverse_{link_type}"))
                conn.commit()
        else:
            logger.warning(f"Failed to link {source_uid} -> {target_uid}: One or both missing.")

    def get_neighborhood(self, uid: str, depth: int = 1) -> List[GraphObject]:
        """Returns the local graph cluster for a given node."""
        if uid not in self.objects:
            return []
        
        cluster = {uid: self.objects[uid]}
        queue = [(uid, 0)]
        
        while queue:
            current_uid, current_depth = queue.pop(0)
            if current_depth >= depth:
                continue
                
            for neighbor_uid, _ in self.objects[current_uid].links:
                if neighbor_uid not in cluster and neighbor_uid in self.objects:
                    cluster[neighbor_uid] = self.objects[neighbor_uid]
                    queue.append((neighbor_uid, current_depth + 1))
        
        return list(cluster.values())

    def ingest_symbol(self, rel_path: str, name: str, symbol_type: str, properties: Dict[str, Any]):
        uid = f"symbol:{rel_path}:{name}"
        obj = GraphObject(uid=uid, type="symbol", properties={
            "name": name,
            "file_path": rel_path,
            "symbol_type": symbol_type,
            **properties
        })
        self.upsert_object(obj)
        
        # Link to module
        module_uid = f"module:{rel_path}"
        if module_uid not in self.objects:
            self.upsert_object(GraphObject(uid=module_uid, type="module", properties={"name": rel_path}))
        self.link(module_uid, uid, "defines")
        return uid

    def ingest_intent(self, intent_id: str, content: str, properties: Dict[str, Any]):
        uid = f"intent:{intent_id}"
        obj = GraphObject(uid=uid, type="intent", properties={
            "content": content,
            **properties
        })
        self.upsert_object(obj)
        
        # Link to specific symbol if provided in properties
        if "focus_symbol" in properties:
            symbol_uid = properties['focus_symbol']
            if symbol_uid in self.objects:
                self.link(uid, symbol_uid, "clarifies")
        
        # Link to module if file_path is provided
        if "file_path" in properties:
            module_uid = f"module:{properties['file_path']}"
            if module_uid not in self.objects:
                self.upsert_object(GraphObject(uid=module_uid, type="module", properties={"name": properties['file_path']}))
            self.link(uid, module_uid, "described_in")
                
        return uid

    def ingest_finding(self, rel_path: str, finding_type: str, severity: str, message: str, properties: Dict[str, Any]):
        uid = f"finding:{rel_path}:{finding_type}:{datetime.now().timestamp()}"
        obj = GraphObject(uid=uid, type="finding", properties={
            "finding_type": finding_type,
            "severity": severity,
            "message": message,
            "file_path": rel_path,
            **properties
        })
        self.upsert_object(obj)
        
        # Link to module
        module_uid = f"module:{rel_path}"
        if module_uid not in self.objects:
            self.upsert_object(GraphObject(uid=module_uid, type="module", properties={"name": rel_path}))
        self.link(uid, module_uid, "violates")
        
        # Link to specific symbol if provided in properties
        if "focus_symbol" in properties:
            symbol_uid = f"symbol:{rel_path}:{properties['focus_symbol']}"
            if symbol_uid in self.objects:
                self.link(uid, symbol_uid, "targets")
                
        return uid

    def _load(self):
        """Load state from SQLite."""
        if not Path(self.storage_path).exists():
            return
            
        with sqlite3.connect(self.storage_path) as conn:
            # Load objects
            rows = conn.execute("SELECT uid, type, data, created_at FROM objects").fetchall()
            for uid, type_name, data_json, created_at in rows:
                self.objects[uid] = GraphObject(
                    uid=uid, 
                    type=type_name, 
                    properties=json.loads(data_json),
                    created_at=created_at
                )
            
            # Load links
            rows = conn.execute("SELECT source, target, type FROM links").fetchall()
            for source, target, link_type in rows:
                if source in self.objects:
                    self.objects[source].add_link(target, link_type)
