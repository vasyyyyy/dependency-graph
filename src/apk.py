"""Download and parse Alpine APKINDEX metadata."""

import gzip
import io
import tarfile
import urllib.error
import urllib.request

TIMEOUT_SECONDS = 30
INDEX_NAME = "APKINDEX"


class RepositoryError(Exception):
    """An error while reading repository metadata."""


def download(url):
    """Download repository metadata without package managers."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "DependencyGraphStudent/1.0"},
    )
    try:
        with urllib.request.urlopen(
            request, timeout=TIMEOUT_SECONDS
        ) as response:
            return response.read()
    except (OSError, ValueError) as error:
        raise RepositoryError(
            f"cannot download repository: {error}"
        ) from error


def extract_index(data):
    """Read APKINDEX from a gzip archive entirely in memory."""
    try:
        unpacked = gzip.decompress(data)
        with tarfile.open(
            fileobj=io.BytesIO(unpacked),
            mode="r:",
            ignore_zeros=True,
        ) as archive:
            member = next(
                (
                    item for item in archive.getmembers()
                    if item.name.lstrip("./") == INDEX_NAME
                    and item.isfile()
                ),
                None,
            )
            if member is None:
                raise RepositoryError("APKINDEX file is missing")
            handle = archive.extractfile(member)
            if handle is None:
                raise RepositoryError("cannot read APKINDEX")
            with handle:
                return handle.read().decode("utf-8")
    except (OSError, EOFError, tarfile.TarError, UnicodeError) as error:
        raise RepositoryError(
            f"invalid APKINDEX archive: {error}"
        ) from error


def parse_index(text):
    """Convert blank-line-separated records into dictionaries."""
    records = []
    current = {}
    for line in text.splitlines() + [""]:
        if not line.strip():
            if "P" in current and "V" in current:
                records.append(current)
            current = {}
            continue
        key, separator, value = line.partition(":")
        if separator:
            current[key] = value
    if not records:
        raise RepositoryError("index contains no valid package records")
    return records


def find_package(records, name, version):
    """Find a package by its exact name and version."""
    available = []
    for record in records:
        if record["P"] != name:
            continue
        if record["V"] == version:
            return record
        available.append(record["V"])
    if available:
        versions = ", ".join(sorted(set(available)))
        raise RepositoryError(
            f"version '{version}' of '{name}' not found; "
            f"available versions: {versions}"
        )
    raise RepositoryError(f"package '{name}' not found")


def direct_dependencies(record):
    """Return requirements, preserving their version constraints."""
    dependencies = []
    for item in record.get("D", "").split():
        if item.startswith("!"):
            continue
        if item not in dependencies:
            dependencies.append(item)
    return dependencies


def get_dependencies(url, name, version):
    """Download metadata and return direct package requirements."""
    text = extract_index(download(url))
    records = parse_index(text)
    record = find_package(records, name, version)
    return direct_dependencies(record)