"""Check the exact source workbook versions recorded in the manifest."""

import hashlib
import json
from pathlib import Path


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_sources(project_dir):
    """Return verified manifest entries or fail on missing/changed files."""
    project_dir = Path(project_dir)
    manifest = json.loads((project_dir / "docs" / "data_sources.json").read_text(encoding="utf-8"))
    verified = []
    for entry in manifest["files"]:
        path = project_dir / entry["path"]
        if not path.is_file():
            raise FileNotFoundError(f"Missing source workbook: {entry['path']}")
        if path.stat().st_size != entry["bytes"] or file_sha256(path) != entry["sha256"]:
            raise ValueError(f"Source workbook differs from manifest: {entry['path']}")
        verified.append(dict(entry))
    return verified
