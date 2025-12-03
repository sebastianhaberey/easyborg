import argparse
import socket
import subprocess
import textwrap
from importlib.metadata import PackageNotFoundError, requires, version
from pathlib import Path

import requests
import urllib3
from packaging.markers import default_environment
from packaging.requirements import Requirement


def allowed_gai_family():
    return socket.AF_INET  # Force IPv4


urllib3.util.connection.allowed_gai_family = allowed_gai_family


def run(*cmd):
    return subprocess.check_output(cmd, text=True).strip()


def major_minor(python_version: str) -> str:
    return ".".join(python_version.split(".")[:2])


def get_package_info(name: str, version: str, root: bool = False):
    """
    Return (url, sha256) preferring wheel files, then falling back to sdist.
    Wheels install much faster inside Homebrew virtualenvs.
    """
    print(f"Querying PyPI for {name} version {version}")

    meta = requests.get(
        f"https://pypi.org/pypi/{name}/{version}/json",
        timeout=10,
    ).json()
    files = meta["urls"]

    if not root:
        for file in files:
            if file["packagetype"] == "bdist_wheel" and file["filename"].endswith("py3-none-any.whl"):
                print(f"Using universal wheel for {file['filename']}")
                return file["url"], file["digests"]["sha256"]

        for file in files:
            if file["packagetype"] == "bdist_wheel":
                print(f"Using wheel for {file['filename']}")
                return file["url"], file["digests"]["sha256"]

    for file in files:
        if file["packagetype"] == "sdist":
            print(f"Using sdist for {file['filename']}")
            return file["url"], file["digests"]["sha256"]

    raise RuntimeError(f"No bdist_wheel found on PyPI for {name}=={version}")


def build_marker_env(target_version: str):
    """Builds an environment to filter out dependencies based on markers"""
    env = default_environment()
    env["extra"] = None
    env["python_version"] = major_minor(target_version)
    env["python_full_version"] = target_version
    return env


def resolve_dependencies(root_package: str, python_version: str) -> dict:
    """Return {package: version} for root_package and all transitive runtime deps."""
    resolved = {}
    stack = [root_package]

    env = build_marker_env(python_version)

    while stack:
        package = stack.pop()

        try:
            ver = version(package)
        except PackageNotFoundError:
            raise RuntimeError(f"Dependency '{package}' is not installed in the current environment.")

        if package in resolved:
            continue

        resolved[package] = ver

        requirements = requires(package) or []
        for r in requirements:
            requirement = Requirement(r)
            if requirement.marker is not None and not requirement.marker.evaluate(env):
                continue
            dep_name = requirement.name
            stack.append(dep_name)

    return resolved


def get_metadata(dep_map: dict, root: str) -> dict:
    """
    Convert {pkg: version} → {
        pkg: { "version": ..., "url": ..., "sha256": ... }
    }
    """
    enriched = {}

    for package, ver in dep_map.items():
        url, sha = get_package_info(package, ver, package == root)
        enriched[package] = {
            "version": ver,
            "url": url,
            "sha256": sha,
        }

    return enriched


def generate_formula(package: str, template: str, all_metadata: dict, python_version: str) -> str:
    """Generates the formula for the given package."""
    resource_blocks = []
    for name, metadata in sorted(all_metadata.items()):
        if name.lower() == package.lower():
            continue

        block = textwrap.dedent(f"""
        resource "{name}" do
          url "{metadata["url"]}"
          sha256 "{metadata["sha256"]}"
        end
        """).strip()
        block = textwrap.indent(block, "  ")
        resource_blocks.append(block)

    resources_text = "\n\n".join(resource_blocks)

    metadata = all_metadata[package]
    return (
        template.replace("{{URL}}", metadata["url"])
        .replace("{{SHA256}}", metadata["sha256"])
        .replace("{{RESOURCES}}", resources_text)
        .replace("{{PYTHON_VERSION}}", major_minor(python_version))
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--python-version", required=True)
    parser.add_argument("--template", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    package = args.package
    version = args.version

    # Resolve dependencies based on installed packages in current venv
    print("Resolving dependencies…")
    dependency_map = resolve_dependencies(package, args.python_version)

    # Replace root package local version with the release version
    # (the installed version might not match the release tag)
    dependency_map[package] = version

    # Enrich with PyPI metadata
    print("Fetching PyPI metadata…")
    all_metadata = get_metadata(dependency_map, package)

    # Apply template
    print("Generating formula…")
    formula = generate_formula(package, Path(args.template).read_text(), all_metadata, args.python_version)

    Path(args.output).write_text(formula)
    print(f"Formula written to {args.output}")


if __name__ == "__main__":
    main()
