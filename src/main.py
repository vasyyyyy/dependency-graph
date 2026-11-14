"""Command-line entry point for the dependency tool."""

import argparse
import sys

from apk import RepositoryError, get_dependencies
from config import ConfigError, load_config


def parse_args(argv=None):
    """Read the configuration path and demonstration mode."""
    parser = argparse.ArgumentParser(
        description="Alpine package dependency tool"
    )
    parser.add_argument(
        "--config",
        default="config.toml",
        help="path to the TOML configuration",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="show settings without downloading metadata",
    )
    return parser.parse_args(argv)


def print_config(config):
    """Print all user settings as key-value pairs."""
    for key, value in vars(config).items():
        print(f"{key} = {value}")


def print_dependencies(config, dependencies):
    """Display direct requirements of the selected package."""
    print(
        f"Direct dependencies of "
        f"{config.package} {config.version}:"
    )
    if not dependencies:
        print("  No direct dependencies.")
        return
    for dependency in dependencies:
        print(f"  {dependency}")


def main(argv=None):
    """Run the application and return its exit code."""
    args = parse_args(argv)
    try:
        config = load_config(args.config)
        if args.show_config:
            print_config(config)
            return 0
        if config.test_mode:
            raise RepositoryError(
                "test repository graphs belong to stage 3; "
                "use test_mode = false for stage 2"
            )
        dependencies = get_dependencies(
            config.repository, config.package, config.version
        )
        print_dependencies(config, dependencies)
    except (ConfigError, RepositoryError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())