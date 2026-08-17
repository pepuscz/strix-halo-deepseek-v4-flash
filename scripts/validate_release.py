#!/usr/bin/env python3
"""Fail closed on malformed release pins or likely public-data leaks."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml


HEX64 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_ARTIFACT_HOSTS = {"github.com", "huggingface.co", "archive.ubuntu.com"}
TEXT_SUFFIXES = {"", ".cfg", ".in", ".j2", ".json", ".md", ".py", ".sh", ".txt", ".yml", ".yaml"}
FORBIDDEN_PUBLIC_PATTERNS = {
    "macOS home path": re.compile(r"/Users/[^/\s]+/"),
    "private IPv4 address": re.compile(r"(?<![0-9])(?:10|192\.168)\.(?:[0-9]{1,3}\.){2}[0-9]{1,3}(?![0-9])"),
    "SSH private key": re.compile(r"BEGIN (?:OPENSSH|RSA|EC|DSA) PRIVATE KEY"),
    "Ansible inline password": re.compile(r"ansible_(?:password|become_pass|ssh_pass)\s*:", re.I),
}


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def require_sha(value: object, label: str) -> None:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        fail(f"{label} is not a lowercase SHA-256")


def require_url(value: object, label: str) -> None:
    parsed = urlparse(str(value))
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_ARTIFACT_HOSTS:
        fail(f"{label} is not an allowed HTTPS publisher URL: {value}")


def validate_manifest(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("deepseek_release_schema") != 1:
        fail("unsupported deepseek_release_schema")
    if data["deepseek_service"]["context"] != 131072:
        fail("selected release must allocate exactly 131072 tokens")
    if data["deepseek_service"]["minimum_effective_non_cma_kib"] < 4 * 1024 * 1024:
        fail("effective non-CMA memory floor is below 4 GiB")
    if data["deepseek_service"]["memory_high"] != "118G" or data["deepseek_service"]["memory_max"] != "120G":
        fail("cgroup memory envelope drifted")
    if data["deepseek_service"]["memory_swap_max"] != 0:
        fail("swap must remain disabled")
    if len(data["deepseek_target"]["shards"]) != 4:
        fail("target must contain four shards")
    shard_total = sum(item["size"] for item in data["deepseek_target"]["shards"])
    if shard_total != data["deepseek_target"]["total_size"]:
        fail(f"target shard total {shard_total} does not match declared total")
    require_url(data["deepseek_runtime"]["archive_url"], "runtime archive_url")
    require_url(data["deepseek_vulkan_loader"]["url"], "Vulkan loader URL")
    for key in ("archive_sha256", "manifest_sha256", "launcher_sha256", "server_sha256"):
        require_sha(data["deepseek_runtime"][key], f"runtime {key}")
    for key in ("sha256", "library_sha256"):
        require_sha(data["deepseek_vulkan_loader"][key], f"Vulkan loader {key}")
    for index, shard in enumerate(data["deepseek_target"]["shards"], start=1):
        require_sha(shard["sha256"], f"target shard {index}")
    require_sha(data["deepseek_draft"]["sha256"], "draft")
    require_sha(data["deepseek_ryzenadj"]["tested_binary_sha256"], "RyzenAdj binary")
    if data.get("deepseek_artifact_seed_paths") or data.get("deepseek_runtime_archive_seed_path"):
        fail("public release manifest contains machine-local artifact seeds")
    if data.get("deepseek_vulkan_loader_seed_path"):
        fail("public release manifest contains a machine-local Vulkan loader seed")
    return data


def scan_public_tree(root: Path) -> None:
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts or path.suffix not in TEXT_SUFFIXES:
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        if path.stat().st_size > 2_000_000:
            fail(f"unexpected large text file: {path.relative_to(root)}")
        text = path.read_text(encoding="utf-8")
        for label, pattern in FORBIDDEN_PUBLIC_PATTERNS.items():
            if pattern.search(text):
                fail(f"possible {label} in {path.relative_to(root)}")


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: validate_release.py RELEASE.yml")
    manifest = Path(sys.argv[1]).resolve()
    root = Path(__file__).resolve().parents[1]
    data = validate_manifest(manifest)
    scan_public_tree(root)
    summary = {
        "release": data["deepseek_release_id"],
        "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "target_bytes": data["deepseek_target"]["total_size"],
        "draft_bytes": data["deepseek_draft"]["size"],
        "public_tree_scan": "passed",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
