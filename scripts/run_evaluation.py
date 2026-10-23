"""Execute the main experiment with this Python environment in a fresh kernel."""

import argparse
from pathlib import Path
import sys

from jupyter_client import KernelManager
import nbformat
from nbclient import NotebookClient

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from src.provenance import verify_sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--timeout", type=int, default=300,
        help="Maximum seconds per code cell (default: 300).",
    )
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")

    project_dir = PROJECT_DIR
    try:
        verified = verify_sources(project_dir)
    except (OSError, ValueError) as exc:
        print(f"Data verification failed: {exc}", file=sys.stderr)
        print("Restore the workbooks recorded in docs/data_sources.json before running.", file=sys.stderr)
        return 1
    print(f"Verified {len(verified)} source workbook hashes.", flush=True)
    source = project_dir / "notebooks" / "03_calendar_model.ipynb"
    report_dir = project_dir / "reports"
    report_dir.mkdir(exist_ok=True)
    output = report_dir / "03_calendar_model.executed.ipynb"
    failed_output = report_dir / "03_calendar_model.failed.ipynb"

    notebook = nbformat.read(source, as_version=4)
    nbformat.validate(notebook)
    for cell in notebook.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None

    # Use the interpreter that launched this script, even if the registered
    # python3 kernel points to another environment.
    manager = KernelManager(kernel_name="python3")
    manager.kernel_spec.argv = [
        sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}",
    ]
    client = NotebookClient(
        notebook,
        km=manager,
        timeout=args.timeout,
        allow_errors=False,
        resources={"metadata": {"path": str(project_dir)}},
    )
    print(f"Executing: {source.name}", flush=True)
    print(f"Python: {sys.executable}", flush=True)
    try:
        # This script supplied the manager, so explicitly request cleanup.
        client.execute(cleanup_kc=True)
        nbformat.validate(notebook)
    except Exception as exc:
        nbformat.write(notebook, failed_output)
        print(f"Evaluation failed: {exc}", file=sys.stderr)
        print(f"Partial notebook: {failed_output}", file=sys.stderr)
        print("Any existing executed report is from an earlier run.", file=sys.stderr)
        return 1

    nbformat.write(notebook, output)
    count = sum(cell.cell_type == "code" for cell in notebook.cells)
    print(f"Completed {count} code cells. Saved: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
