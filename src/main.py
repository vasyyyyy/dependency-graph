"""Entry point of the dependency graph tool."""
import argparse
import sys

from config import ConfigError, load_config


def parse_args(argv=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Dependency graph visualizer"
    )
    parser.add_argument(
        "--config", default="config.toml", help="path to the TOML config"
    )
    return parser.parse_args(argv)


def print_config(config):
    """Print all parameters as key-value pairs."""
    for key, value in vars(config).items():
        print(f"{key} = {value}")


def main(argv=None):
    """Run the tool and return the exit code."""
    args = parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print_config(config)
    return 0


if __name__ == "__main__":
    sys.exit(main())