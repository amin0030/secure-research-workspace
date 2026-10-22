
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts import verify_helper_integrity as integrity


class HelperIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)

        self.package = Path(self.temporary.name) / "package"
        self.package.mkdir()

        self.helper = self.package / "helper.py"
        self.helper.write_bytes(b"def result():\n    return True\n")

        self.manifest = Path(self.temporary.name) / "approved_hashes.json"

        with patch.object(integrity, "PACKAGE", self.package):
            approved = integrity.calculate_hashes()

        self.manifest.write_text(json.dumps(approved), encoding="utf-8")

    def run_gate(self):
        output = io.StringIO()

        with (
            patch.object(integrity, "PACKAGE", self.package),
            patch.object(integrity, "MANIFEST", self.manifest),
            patch.object(sys, "argv", ["verify_helper_integrity.py"]),
            redirect_stdout(output),
        ):
            result = integrity.main()

        return result, output.getvalue()

    def test_approved_package_passes(self):
        result, output = self.run_gate()

        self.assertEqual(result, 0)
        self.assertIn("PASS: Helper package matches", output)

    def test_added_file_is_rejected(self):
        (self.package / "UNAPPROVED.txt").write_text("Changed", encoding="utf-8")

        result, output = self.run_gate()

        self.assertEqual(result, 1)
        self.assertIn("FAIL: Unapproved package file: UNAPPROVED.txt", output)

    def test_modified_file_is_rejected(self):
        self.helper.write_bytes(b"def result():\n    return False\n")

        result, output = self.run_gate()

        self.assertEqual(result, 1)
        self.assertIn("FAIL: Unapproved package file: helper.py", output)

    def test_missing_manifest_is_rejected(self):
        self.manifest.unlink()

        result, output = self.run_gate()

        self.assertEqual(result, 1)
        self.assertIn("FAIL: Approved package manifest is missing", output)


if __name__ == "__main__":
    unittest.main()
