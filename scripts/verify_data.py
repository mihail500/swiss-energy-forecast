"""Verify local workbook sizes and SHA-256 hashes against the source manifest."""

from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from src.provenance import verify_sources


def main():
    try:
        entries = verify_sources(PROJECT_DIR)
    except (OSError, ValueError) as exc:
        print(f"Data verification failed: {exc}", file=sys.stderr)
        return 1
    for entry in entries:
        print(f"Verified: {entry['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
