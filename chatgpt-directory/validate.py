#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["jsonschema>=4,<5"]
# ///
"""Validate the portable package and OpenAI submission fields before making a ZIP.

The portable schemas allow arbitrary extensions, so they cannot catch a wrong
OpenAI review field type. Keep those checks beside the submission package.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import zipfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

import jsonschema

ROOT = Path(__file__).resolve().parent
DOCS = "https://developers.openai.com/plugins/deploy/submission"
# The video host (Cloudflare R2) answers 403 to Python-urllib's default agent.
USER_AGENT = "Postory-Review-Validator/1.0"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def https(value, field):
    require(isinstance(value, str), f"{field} must be a string")
    parsed = urlsplit(value)
    require(parsed.scheme == "https" and parsed.hostname and not parsed.username
            and not parsed.password and not parsed.fragment,
            f"{field} must be an HTTPS URL without credentials or fragments")


def text(value, field, limit):
    require(isinstance(value, str) and value.strip() and len(value) <= limit,
            f"{field} must be nonempty text, at most {limit} characters")


def asset(value):
    require(isinstance(value, str) and value.startswith("./assets/"),
            "icons must be ./assets/ paths")
    path = (ROOT / value).resolve()
    require(path.is_relative_to(ROOT) and path.is_file(), f"Missing asset: {value}")
    raw = path.read_bytes()
    require(len(raw) <= 5 * 1024 * 1024, f"Asset too large: {value}")
    # This package ships PNGs. Fail if its image changes to an unvalidated type.
    require(raw.startswith(b"\x89PNG\r\n\x1a\n"), f"Expected a PNG: {value}")
    width, height = struct.unpack(">II", raw[16:24])
    require(width == height and 48 <= width <= 4096,
            f"Icon must be square, 48–4096 pixels: {value}")
    return path


def portable_schema(document):
    with urlopen(document["$schema"], timeout=30) as response:
        schema = json.load(response)
    jsonschema.Draft202012Validator(schema).validate(document)


def video_accessible(url):
    """HEAD once; only method-not-supported falls back to a one-byte GET."""
    try:
        with urlopen(Request(url, method="HEAD", headers={"User-Agent": USER_AGENT}), timeout=30) as response:
            require(200 <= response.status < 300, "Reviewer video URL is inaccessible")
    except HTTPError as exc:
        if exc.code not in (405, 501):
            raise
        exc.close()
        with urlopen(Request(url, headers={"Range": "bytes=0-0", "User-Agent": USER_AGENT}), timeout=30) as response:
            require(200 <= response.status < 300, "Reviewer video URL is inaccessible")
            response.read(1)  # Bound transfer even when the host ignores Range.


def validate(manifest, mcp, *, allow_missing_video=False):
    portable_schema(manifest)
    portable_schema(mcp)
    require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", manifest["name"])
            and len(manifest["name"]) <= 64, "Invalid submission package name")
    require(re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]), "Use a semantic version")
    text(manifest["description"], "description", 4000)
    ext = manifest["extensions"]["com.openai"]
    require(not {"apps", "hooks", "test_credentials", "reviewer_instructions"} & ext.keys(),
            "Public package must not include app references, hooks or credentials")
    ui = ext["interface"]
    for key, limit in {"displayName": 30, "shortDescription": 30,
                       "longDescription": 4000, "developerName": 80}.items():
        text(ui.get(key), key, limit)
    text(ui.get("category"), "category", 80)
    for key in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
        https(ui.get(key), key)
        require(len(ui[key]) <= 1024, f"{key} exceeds 1024 characters")
    prompts = ui.get("defaultPrompt", [])
    prompts = [prompts] if isinstance(prompts, str) else prompts
    require(isinstance(prompts, list) and len(prompts) <= 3, "At most three starter prompts")
    require(len(prompts) == len(set(prompts)), "Starter prompts must be unique")
    for prompt in prompts:
        text(prompt, "defaultPrompt", 128)
    assets = {asset(ui.get(key)) for key in ("logo", "composerIcon")}
    servers = mcp["mcpServers"]
    require(len(servers) == 1, "Plugin-level review cases require exactly one MCP server")
    server = next(iter(servers.values()))
    require(server["type"] == "streamable-http", "Public submission needs remote HTTP MCP")
    https(server["url"], "MCP URL")
    require(not server.get("headers"), "Do not package authentication headers")
    require(server["url"] == "https://postory.io/mcp",
            "Use Postory's canonical OAuth-discoverable endpoint")
    review = ext["review"]
    cases = review["test_cases"]
    for kind, count in (("positive", 5), ("negative", 3)):
        require(isinstance(cases.get(kind), list) and len(cases[kind]) == count,
                f"Exactly {count} {kind} cases required")
        for case in cases[kind]:
            for key in ("description", "prompt"):
                text(case.get(key), f"{kind}.{key}", 4000)
            if kind == "positive":
                text(case.get("tools_triggered"), "tools_triggered", 4000)
                require(all(re.fullmatch(r"[a-z][a-z0-9_]*", name.strip())
                            for name in case["tools_triggered"].split(",")),
                        "tools_triggered must be comma-separated tool names")
                text(case.get("expected_behavior"), "expected_behavior", 4000)
    require(review.get("commerce") is False, "This package must not offer commerce")
    video = review.get("demo_recording_url")
    if video:
        https(video, "demo_recording_url")
        video_accessible(video)
    else:
        require(allow_missing_video, "Missing reviewer video: add review.demo_recording_url before submission")
    publication = ext["publication"]
    text(publication.get("release_notes"), "release_notes", 4000)
    require(all(isinstance(c, str) and re.fullmatch(r"[A-Z]{2}", c)
                for c in publication.get("countries", [])), "Use uppercase ISO country codes")
    return assets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-url", help="Use the verified public video URL in the built manifest")
    parser.add_argument("--allow-missing-video", action="store_true", help="Check draft metadata only; cannot build a ZIP")
    parser.add_argument("--zip", type=Path, help="Write only plugin.json, mcp.json and assets after validation")
    args = parser.parse_args()
    require(not (args.zip and args.allow_missing_video), "Final ZIP validation must require the video")
    manifest = json.loads((ROOT / "plugin.json").read_text())
    mcp = json.loads((ROOT / "mcp.json").read_text())
    if args.demo_url:
        manifest["extensions"]["com.openai"]["review"]["demo_recording_url"] = args.demo_url
    assets = validate(manifest, mcp, allow_missing_video=args.allow_missing_video)
    if args.zip:
        with zipfile.ZipFile(args.zip, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("plugin.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
            archive.writestr("mcp.json", json.dumps(mcp, indent=2) + "\n")
            for path in sorted(assets):
                archive.write(path, path.relative_to(ROOT))
        with zipfile.ZipFile(args.zip) as archive:
            require(archive.testzip() is None, "ZIP checksum check failed")
        print(f"PASS: submission package written to {args.zip}")
    else:
        print("PASS: draft metadata (video still required)" if args.allow_missing_video else "PASS: submission metadata")
    print(f"Official field reference: {DOCS}")


def cli():
    try:
        main()
    except (ValueError, KeyError, OSError, URLError, jsonschema.ValidationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(cli())
