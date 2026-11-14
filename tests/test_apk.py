"""Offline tests for Alpine repository metadata."""

import gzip
import io
import sys
import tarfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from apk import (
    RepositoryError,
    direct_dependencies,
    extract_index,
    find_package,
    parse_index,
)

SAMPLE = (
    "P:app\n"
    "V:1.0-r0\n"
    "D:lib>=2.0 so:libc.so !bad lib>=2.0\n"
    "\n"
    "P:lib\n"
    "V:2.1-r0\n"
    "\n"
)


class ApkTests(unittest.TestCase):
    """Check parsing, exact versions and error handling."""

    def test_parse(self):
        """Read two package records."""
        self.assertEqual(len(parse_index(SAMPLE)), 2)

    def test_exact_version(self):
        """Find the exact requested version."""
        record = find_package(
            parse_index(SAMPLE), "app", "1.0-r0"
        )
        self.assertEqual(record["P"], "app")

    def test_dependencies(self):
        """Preserve constraints and exclude conflicts."""
        record = find_package(
            parse_index(SAMPLE), "app", "1.0-r0"
        )
        self.assertEqual(
            direct_dependencies(record),
            ["lib>=2.0", "so:libc.so"],
        )

    def test_no_dependencies(self):
        """A package without D has no dependencies."""
        record = find_package(
            parse_index(SAMPLE), "lib", "2.1-r0"
        )
        self.assertEqual(direct_dependencies(record), [])

    def test_unknown_package(self):
        """Reject a package absent from the index."""
        with self.assertRaises(RepositoryError):
            find_package(parse_index(SAMPLE), "missing", "1.0")

    def test_unknown_version(self):
        """Report versions available in the selected index."""
        with self.assertRaisesRegex(
            RepositoryError, "available versions"
        ):
            find_package(parse_index(SAMPLE), "app", "9.9")

    def test_invalid_index(self):
        """Reject text without valid package records."""
        with self.assertRaises(RepositoryError):
            parse_index("invalid metadata")

    def test_invalid_archive(self):
        """Reject bytes which are not a gzip archive."""
        with self.assertRaises(RepositoryError):
            extract_index(b"not an archive")

    def test_extract_archive(self):
        """Read APKINDEX from a generated in-memory archive."""
        data = SAMPLE.encode("utf-8")
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w") as archive:
            member = tarfile.TarInfo("APKINDEX")
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))
        compressed = gzip.compress(buffer.getvalue())
        self.assertEqual(extract_index(compressed), SAMPLE)


if __name__ == "__main__":
    unittest.main()