"""Loading and validation of the TOML configuration."""
import tomllib
from dataclasses import dataclass
from pathlib import Path

MIN_DEPTH = 0
URL_PREFIXES = ("http://", "https://")
REQUIRED_KEYS = {
    "package": str,
    "repository": str,
    "test_mode": bool,
    "version": str,
    "ascii_tree": bool,
    "max_depth": int,
}


class ConfigError(Exception):
    """Raised when the configuration is missing or invalid."""


@dataclass
class Config:
    """User-defined settings of the tool."""

    package: str
    repository: str
    test_mode: bool
    version: str
    ascii_tree: bool
    max_depth: int


def read_toml(path):
    """Read a TOML file and return its content as a dict."""
    file = Path(path)
    if not file.is_file():
        raise ConfigError(f"config file not found: {path}")
    try:
        with file.open("rb") as handle:
            return tomllib.load(handle)
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"invalid TOML: {error}") from error


def check_types(data):
    """Check that all keys exist and have the expected types."""
    for key, expected in REQUIRED_KEYS.items():
        if key not in data:
            raise ConfigError(f"missing parameter: {key}")
        value = data[key]
        is_bool_as_int = expected is int and isinstance(value, bool)
        if not isinstance(value, expected) or is_bool_as_int:
            raise ConfigError(
                f"parameter '{key}' must be {expected.__name__}"
            )


def check_values(data):
    """Check the content of the parameters."""
    for key in ("package", "version"):
        if not data[key].strip():
            raise ConfigError(f"parameter '{key}' must not be empty")
    if data["max_depth"] < MIN_DEPTH:
        raise ConfigError("parameter 'max_depth' must not be negative")
    repository = data["repository"]
    if data["test_mode"]:
        if not Path(repository).is_file():
            raise ConfigError(f"test repository not found: {repository}")
    elif not repository.startswith(URL_PREFIXES):
        raise ConfigError("repository must be an http(s) URL")


def load_config(path):
    """Load and validate the configuration file."""
    data = read_toml(path)
    check_types(data)
    check_values(data)
    return Config(**{key: data[key] for key in REQUIRED_KEYS})