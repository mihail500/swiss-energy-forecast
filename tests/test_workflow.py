"""Integrity and runner failure checks using tiny temporary fixtures."""

import contextlib
import hashlib
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

import nbformat

from src.provenance import verify_sources
from src.reporting import _check_reference
import pandas as pd


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "docs").mkdir()
        self.workbook = self.root / "example.xlsx"
        self.workbook.write_bytes(b"original")
        entry = {"path": "example.xlsx", "bytes": 8, "sha256": hashlib.sha256(b"original").hexdigest()}
        (self.root / "docs/data_sources.json").write_text(json.dumps({"files": [entry]}), encoding="utf-8")

    def test_original_source_verified(self):
        self.assertEqual(len(verify_sources(self.root)), 1)

    def test_same_size_changed_source_rejected_by_hash(self):
        self.workbook.write_bytes(b"modified")
        with self.assertRaisesRegex(ValueError, "differs from manifest"):
            verify_sources(self.root)

    def test_missing_source_rejected(self):
        self.workbook.rename(self.root / "moved.xlsx")
        with self.assertRaisesRegex(FileNotFoundError, "Missing source"):
            verify_sources(self.root)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.main = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/run_evaluation.py"))["main"]

    def test_failed_preflight_does_not_start_a_kernel(self):
        with patch.object(sys, "argv", ["run_evaluation.py"]), patch.dict(self.main.__globals__, {"verify_sources": unittest.mock.Mock(side_effect=ValueError("changed source"))}), patch("nbclient.NotebookClient.execute") as execute, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.main(), 1)
            execute.assert_not_called()

    def test_failed_execution_preserves_source_and_prior_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "notebooks").mkdir()
            (root / "reports").mkdir()
            source = root / "notebooks/03_calendar_model.ipynb"
            notebook = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("raise RuntimeError('failure')")])
            nbformat.write(notebook, source)
            source_bytes = source.read_bytes()
            successful = root / "reports/03_calendar_model.executed.ipynb"
            successful.write_text("earlier successful report", encoding="utf-8")
            with patch.object(sys, "argv", ["run_evaluation.py"]), patch.dict(self.main.__globals__, {"PROJECT_DIR": root, "verify_sources": lambda _: []}), patch("nbclient.NotebookClient.execute", side_effect=RuntimeError("simulated failure")), contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(self.main(), 1)
            self.assertEqual(source.read_bytes(), source_bytes)
            self.assertEqual(successful.read_text(encoding="utf-8"), "earlier successful report")
            partial = nbformat.read(root / "reports/03_calendar_model.failed.ipynb", as_version=4)
            nbformat.validate(partial)
            self.assertIsNone(partial.cells[0].execution_count)

    def test_invalid_timeout_rejected(self):
        with patch.object(sys, "argv", ["run_evaluation.py", "--timeout", "0"]), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                self.main()
            self.assertEqual(raised.exception.code, 2)


class ReferenceTests(unittest.TestCase):
    def test_changed_score_fails_checkpoint_check(self):
        scores = pd.DataFrame([[10., 12., -1.]], index=["model"])
        with self.assertRaises(AssertionError):
            _check_reference(scores, {"model": [9., 12., -1.]})


if __name__ == "__main__":
    unittest.main()
