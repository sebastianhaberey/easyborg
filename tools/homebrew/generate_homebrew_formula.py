#!/usr/bin/env python3
from __future__ import annotations

import argparse
import socket
import textwrap
from pathlib import Path

import requests
import urllib3
from packaging.markers import Environment, default_environment
from packaging.requirements import Requirement
from packaging.version import Version


def allowed_gai_family():
    return socket.AF_INET  # Force IPv4


# Force urllib3 to use IPv4
urllib3.util.connection.allowed_gai_family = allowed_gai_family


def major_minor(pyver: str) -> str:
    return ".".join(pyver.split(".")[:2])


def fetch_pypi_metadata(package: str, version: str | None = None) -> dict:
    """Fetch PyPI JSON for package, optionally pinned to version."""
    if version:
        url = f"https://pypi.org/pypi/{package}/{version}/json"
    else:
        url = f"https://pypi.org/pypi/{package}/json"

    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"Could not fetch PyPI metadata for {package} (version={version})")

    return resp.json()


def get_url(meta: dict, packagetype: str) -> dict:
    """
    Choose best download url from metadata: prefers py3-none-any wheels, then other wheels, then sdist.
    """
    for url in meta["urls"]:
        if url["packagetype"] == packagetype:
            return url

    raise RuntimeError(f"No usable distribution for root package {meta['info']['name']}.")


def build_marker_env(target_python_version: str) -> Environment:
    """Environment for PEP 508 marker evaluation."""
    env = default_environment()
    env["python_version"] = major_minor(target_python_version)
    env["python_full_version"] = target_python_version
    env["extra"] = None
    return env


def get_matching_version(metadata: dict, requirement: Requirement) -> str | None:
    if not requirement.specifier:  # no pinned version, return current version
        return metadata["info"]["version"]

    versions = sorted((Version(v) for v in metadata["releases"] if v), reverse=True)
    for version in versions:
        if version in requirement.specifier:
            return str(version)

    raise RuntimeError(f"Could not find version satisfying {requirement} for {requirement.name}")


def resolve_dependencies_from_pypi(root_package: str, root_version: str, python_version: str) -> dict[str, dict]:
    """
    Returns mapping: package -> { "version": ..., "url": ..., "sha256": ... }
    """

    env = build_marker_env(python_version)
    todo = [(root_package, root_version)]
    resolved: dict[str, dict] = {}

    while todo:
        package, version = todo.pop()

        if package in resolved:
            continue

        metadata = fetch_pypi_metadata(package, version)
        info = metadata["info"]
        name = info["name"]

        if name == root_package:
            url = get_url(metadata, "sdist")  # use sdist for root package (required for brew)
        else:
            url = get_url(metadata, "bdist_wheel")  # use wheel for dependencies

        resolved[name] = {"version": version, "url": url["url"], "sha256": url["digests"]["sha256"]}

        requires_dist = info.get("requires_dist") or []
        for requirement_str in requires_dist:
            requirement = Requirement(requirement_str)

            if requirement.marker and not requirement.marker.evaluate(env):
                continue

            metadata = fetch_pypi_metadata(requirement.name)
            version = get_matching_version(metadata, requirement)
            todo.append((requirement.name, version))

    return resolved


def generate_formula(package: str, template: str, metadata: dict, python_version: str) -> str:
    """Generate final formula text."""
    resource_blocks = []

    for name, info in sorted(metadata.items()):
        if name.lower() == package.lower():
            continue

        block = f"""
        resource "{name}" do
          url "{info["url"]}"
          sha256 "{info["sha256"]}"
        end
        """
        resource_blocks.append(textwrap.indent(block.strip(), "  "))

    resources_text = "\n\n".join(resource_blocks)

    root = metadata[package]

    return (
        template.replace("{{URL}}", root["url"])
        .replace("{{SHA256}}", root["sha256"])
        .replace("{{RESOURCES}}", resources_text)
        .replace("{{PYTHON_VERSION}}", major_minor(python_version))
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--package", required=True)
    p.add_argument("--version", required=True)
    p.add_argument("--python-version", required=True)
    p.add_argument("--template", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    print(f"Resolving dependencies for {args.package}=={args.version}…")
    all_meta = resolve_dependencies_from_pypi(
        args.package,
        args.version,
        args.python_version,
    )

    print("Fetching distribution metadata from PyPI…")
    template = Path(args.template).read_text()
    formula = generate_formula(
        args.package,
        template,
        all_meta,
        args.python_version,
    )

    Path(args.output).write_text(formula)
    print(f"Formula written to {args.output}")


if __name__ == "__main__":
    main()
