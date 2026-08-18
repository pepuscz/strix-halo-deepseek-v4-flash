#!/usr/bin/env python3
"""Validate immutable release pins and the public-data boundary."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml


HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_ARTIFACT_HOSTS = {"github.com", "huggingface.co", "archive.ubuntu.com"}
TEXT_SUFFIXES = {"", ".cfg", ".in", ".j2", ".json", ".md", ".patch", ".py", ".sh", ".txt", ".yml", ".yaml"}
SYSTEMS = {
    "vulkan-iq3xxs": ("Vulkan IQ3_XXS", "vulkan"),
    "rocm-rocmfpx": ("ROCm ROCmFPX", "rocm"),
}
FORBIDDEN_PUBLIC_PATTERNS = {
    "macOS home path": re.compile(r"/Users/[^/\s]+/"),
    "private IPv4 address": re.compile(r"(?<![0-9])(?:10|192\.168)\.(?:[0-9]{1,3}\.){2}[0-9]{1,3}(?![0-9])"),
    "SSH private key": re.compile(r"BEGIN (?:OPENSSH|RSA|EC|DSA) PRIVATE KEY"),
    "Ansible inline password": re.compile(r"ansible_(?:password|become_pass|ssh_pass)\s*:", re.I),
    "casual system label": re.compile(r"\bnathan\b", re.I),
    "competition-log label": re.compile(r"\b(?:winner|challenger)\b", re.I),
}


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def require_sha(value: object, label: str, pattern: re.Pattern[str] = HEX64) -> None:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        fail(f"{label} has an invalid digest")


def require_url(value: object, label: str) -> None:
    parsed = urlparse(str(value))
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_ARTIFACT_HOSTS:
        fail(f"{label} is not an allowed HTTPS publisher URL: {value}")


def validate_manifest(path: Path, root: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("deepseek_release_schema") != 1:
        fail("unsupported deepseek_release_schema")

    system = data.get("deepseek_system", {})
    expected = SYSTEMS.get(system.get("id"))
    if expected != (system.get("name"), system.get("engine")):
        fail("non-canonical deepseek_system identity")

    service = data["deepseek_service"]
    if service["context"] != 131072:
        fail("release must allocate exactly 131072 tokens")
    if service["minimum_effective_non_cma_kib"] < 4 * 1024 * 1024:
        fail("effective non-CMA memory floor is below 4 GiB")
    if service["memory_high"] != "118G" or service["memory_max"] != "120G":
        fail("cgroup memory envelope drifted")
    if service["memory_swap_max"] != 0:
        fail("swap must remain disabled")

    target = data["deepseek_target"]
    files = target["files"]
    if not files or sum(item["size"] for item in files) != target["total_size"]:
        fail("target file total does not match declared total_size")
    for index, artifact in enumerate(files, start=1):
        require_sha(artifact["sha256"], f"target file {index}")
    require_sha(data["deepseek_draft"]["sha256"], "draft")
    require_sha(data["deepseek_ryzenadj"]["tested_binary_sha256"], "RyzenAdj binary")
    require_sha(data["deepseek_runtime"]["source_commit"], "runtime source commit", HEX40)
    require_sha(data["deepseek_runtime"]["server_sha256"], "runtime server")

    if system["engine"] == "vulkan":
        if len(files) != 4:
            fail("Vulkan IQ3_XXS requires four target files")
        runtime = data["deepseek_runtime"]
        require_url(runtime["archive_url"], "runtime archive_url")
        require_url(data["deepseek_vulkan_loader"]["url"], "Vulkan loader URL")
        for key in ("archive_sha256", "manifest_sha256", "launcher_sha256"):
            require_sha(runtime[key], f"runtime {key}")
        for key in ("sha256", "library_sha256"):
            require_sha(data["deepseek_vulkan_loader"][key], f"Vulkan loader {key}")
    else:
        if len(files) != 1:
            fail("ROCm ROCmFPX requires one target file")
        runtime = data["deepseek_runtime"]
        rocm = data["deepseek_rocm"]
        require_url(runtime["repository"], "ROCm runtime repository")
        require_sha(runtime["submodule_commit"], "runtime submodule commit", HEX40)
        require_sha(runtime["source_diff_sha256"], "runtime source diff")
        require_sha(rocm["rocwmma_commit"], "rocWMMA commit", HEX40)
        qualified_paths = (
            rocm.get("qualified_source_path"),
            rocm.get("qualified_build_path"),
            rocm.get("qualified_rocwmma_path"),
        )
        if qualified_paths != (
            "/opt/m5/src/lucebox-019-selected-kv",
            "/opt/m5/src/lucebox-019-selected-kv/server/build-selected-kv",
            "/opt/m5/src/rocWMMA-7.1.1",
        ):
            fail("ROCm absolute build paths drifted from the qualified ELF inputs")
        for patch in rocm["patches"]:
            require_sha(patch["sha256"], f"patch {patch['name']}")
            patch_path = root / "patches" / patch["name"]
            if not patch_path.is_file():
                fail(f"missing public patch: {patch['name']}")
            actual = hashlib.sha256(patch_path.read_bytes()).hexdigest()
            if actual != patch["sha256"]:
                fail(f"public patch hash drifted: {patch['name']}")

    if data.get("deepseek_artifact_seed_paths"):
        fail("public manifest contains machine-local artifact seeds")
    if data.get("deepseek_runtime_archive_seed_path"):
        fail("public manifest contains a machine-local runtime seed")
    if data.get("deepseek_vulkan_loader_seed_path"):
        fail("public manifest contains a machine-local Vulkan loader seed")
    return data


def scan_public_tree(root: Path) -> None:
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if not path.is_file() or any(part in {".git", ".venv"} for part in relative.parts):
            continue
        if relative == Path("ansible/inventory/hosts.yml") or path.suffix not in TEXT_SUFFIXES:
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        if path.stat().st_size > 2_000_000:
            fail(f"unexpected large text file: {relative}")
        text = path.read_text(encoding="utf-8")
        for label, pattern in FORBIDDEN_PUBLIC_PATTERNS.items():
            if pattern.search(text):
                fail(f"possible {label} in {relative}")


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: validate_release.py RELEASE.yml")
    manifest = Path(sys.argv[1]).resolve()
    root = Path(__file__).resolve().parents[1]
    data = validate_manifest(manifest, root)
    scan_public_tree(root)
    summary = {
        "release": data["deepseek_release_id"],
        "system": data["deepseek_system"]["name"],
        "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "target_bytes": data["deepseek_target"]["total_size"],
        "draft_bytes": data["deepseek_draft"]["size"],
        "public_tree_scan": "passed",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
