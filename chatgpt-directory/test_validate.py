# /// script
# dependencies = ["jsonschema>=4,<5"]
# ///
"""Focused validator regressions; run with uv run --script test_validate.py."""
import contextlib
import importlib.util
import io
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

SOURCE = Path(__file__).resolve().parent


class Response(io.BytesIO):
    def __init__(self, status=200):
        super().__init__(b"video bytes that must not all be downloaded")
        self.status = status
        self.read_sizes = []

    def read(self, size=-1):
        self.read_sizes.append(size)
        return super().read(size)


class ValidatorTest(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("submission_validator", SOURCE / "validate.py")
        self.v = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.v)
        self.scratch = tempfile.TemporaryDirectory(prefix="postory-package-test-")
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name).resolve()
        for name in ("plugin.json", "mcp.json"):
            shutil.copyfile(SOURCE / name, self.root / name)
        (self.root / "assets").mkdir()
        shutil.copyfile(SOURCE / "assets/logo.png", self.root / "assets/logo.png")
        self.v.ROOT = self.root

    def cli(self, *args):
        output = io.StringIO()
        with patch.object(sys, "argv", ["validate.py", *map(str, args)]), contextlib.redirect_stderr(output), contextlib.redirect_stdout(output):
            result = self.v.cli()
        return result, output.getvalue()

    def test_head_405_falls_back_to_one_byte_get_even_if_range_is_ignored(self):
        self._head_falls_back_to_one_byte_get(405)

    def test_head_501_falls_back_to_one_byte_get_even_if_range_is_ignored(self):
        self._head_falls_back_to_one_byte_get(501)

    def _head_falls_back_to_one_byte_get(self, status):
        calls = []
        response = Response(200)

        def open_url(request, timeout):
            calls.append(request)
            if request.get_method() == "HEAD":
                raise HTTPError(request.full_url, status, "Method unsupported", {}, io.BytesIO())
            return response

        self.v.urlopen = open_url
        self.v.video_accessible("https://media.postory.test/demo.mp4")
        self.assertEqual([r.get_method() for r in calls], ["HEAD", "GET"])
        self.assertEqual(calls[1].get_header("Range"), "bytes=0-0")
        self.assertEqual(response.read_sizes, [1])
        self.assertTrue(response.closed)

    def test_head_403_fails_cleanly_without_retrying(self):
        self.v.portable_schema = lambda _: None
        calls = []

        def denied(request, timeout):
            calls.append(request)
            raise HTTPError(request.full_url, 403, "Forbidden", {}, io.BytesIO())

        self.v.urlopen = denied
        result, output = self.cli("--demo-url", "https://media.postory.test/demo.mp4")
        self.assertEqual(result, 1)
        self.assertIn("FAIL:", output)
        self.assertNotIn("Traceback", output)
        self.assertEqual(len(calls), 1)

    def test_schema_network_failure_is_clean_fail(self):
        def unavailable(*args, **kwargs):
            raise URLError("DNS unavailable")

        self.v.urlopen = unavailable
        result, output = self.cli("--allow-missing-video")
        self.assertEqual(result, 1)
        self.assertIn("FAIL:", output)
        self.assertNotIn("Traceback", output)

    def test_zip_contains_only_deduplicated_validated_manifest_assets(self):
        self.v.portable_schema = lambda _: None
        self.v.video_accessible = lambda _: None
        (self.root / "assets/.DS_Store").write_bytes(b"finder metadata")
        (self.root / "assets/unreferenced.txt").write_text("must not ship")
        target = self.root / "submission.zip"
        result, output = self.cli("--demo-url", "https://media.postory.test/demo.mp4", "--zip", target)
        self.assertEqual(result, 0, output)
        with zipfile.ZipFile(target) as archive:
            self.assertEqual(set(archive.namelist()), {"plugin.json", "mcp.json", "assets/logo.png"})
            self.assertIsNone(archive.testzip())


if __name__ == "__main__":
    unittest.main()
