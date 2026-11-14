"""Tests for configuration loading."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config import ConfigError, load_config  # noqa: E402

VALID = """
package = "curl"
repository = "https://example.com/APKINDEX.tar.gz"
test_mode = false
version = "1.0"
ascii_tree = false
max_depth = 3
"""


class ConfigTests(unittest.TestCase):
    """Check valid and invalid configurations."""

    def load(self, text):
        """Write text to a temp file and load it as config."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.toml"
            path.write_text(text, encoding="utf-8")
            return load_config(path)

    def test_valid(self):
        """A correct config is loaded."""
        self.assertEqual(self.load(VALID).package, "curl")

    def test_missing_key(self):
        """A missing key raises an error."""
        with self.assertRaises(ConfigError):
            self.load(VALID.replace('package = "curl"', ""))

    def test_wrong_type(self):
        """A wrong type raises an error."""
        with self.assertRaises(ConfigError):
            self.load(VALID.replace("max_depth = 3", 'max_depth = "3"'))

    def test_negative_depth(self):
        """A negative depth raises an error."""
        with self.assertRaises(ConfigError):
            self.load(VALID.replace("max_depth = 3", "max_depth = -1"))

    def test_bad_url(self):
        """A non-URL repository raises an error."""
        with self.assertRaises(ConfigError):
            self.load(VALID.replace("https://example.com", "ftp:/x"))

    def test_missing_file(self):
        """A missing config file raises an error."""
        with self.assertRaises(ConfigError):
            load_config("no-such-file.toml")


if __name__ == "__main__":
    unittest.main()