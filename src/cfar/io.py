from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def fingerprint(value: object) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def write_json(path: str | Path, value: object) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+"\n", encoding="utf-8")


def manifest(instance: dict, settings: dict, status: str, seed: int = 0) -> dict:
    from .schema import ROOT

    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True)
    from .schema import spec_path
    import shapely

    package = Path(__file__).resolve().parent
    source_files = sorted(package.glob("*.py")) + [spec_path(name) for name in ("instance.schema.json","enums.json")]
    return {"schema_version": "0.1.0", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "git_revision": revision.stdout.strip() if revision.returncode == 0 else None,
            "git_dirty": bool(dirty.stdout.strip()) if dirty.returncode == 0 else None,
            "source_fingerprints": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files},
            "input_fingerprint": fingerprint(instance), "seed": seed,
            "python": sys.version, "platform": platform.platform(), "machine": platform.machine(),
            "packages": {p: importlib.metadata.version(p) for p in ("jsonschema", "shapely", "numpy")},
            "geos_version":shapely.geos_version_string,
            "settings": settings, "solver_status": status}
