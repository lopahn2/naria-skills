#!/usr/bin/env python3
"""Build a marketplace branch from the canonical skills/ source."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

PLUGIN_NAME = "stt2study-note-pdf"
DESCRIPTION = "강의 녹취록(STT)과 교재 PDF로 다이어그램 중심 학습 노트 PDF를 만든다."


def remove_generated_contents(root: Path) -> None:
    for entry in root.iterdir():
        if entry.name == ".git":
            continue
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()


def copy_skill(source: Path, target: Path) -> None:
    shutil.copytree(source, target, copy_function=shutil.copy2)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_openai(output: Path, source: Path, version: str) -> None:
    write_json(output / ".agents/plugins/marketplace.json", {
        "name": "naria-skills",
        "interface": {"displayName": "Naria Skills"},
        "plugins": [{
            "name": PLUGIN_NAME,
            "source": {"source": "local", "path": f"./plugins/{PLUGIN_NAME}"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        }],
    })
    write_json(output / f"plugins/{PLUGIN_NAME}/.codex-plugin/plugin.json", {
        "name": PLUGIN_NAME,
        "version": version,
        "description": DESCRIPTION,
        "author": {"name": "naria"},
        "skills": "./skills/",
        "interface": {
            "displayName": "STT to Study Note PDF",
            "shortDescription": "STT와 교재 PDF로 학습 노트를 만듭니다.",
            "longDescription": DESCRIPTION,
            "developerName": "naria",
            "category": "Productivity",
            "capabilities": [],
            "defaultPrompt": ["강의 녹취록과 교재 PDF를 바탕으로 학습 노트를 만들어줘."],
        },
    })
    copy_skill(source, output / f"plugins/{PLUGIN_NAME}/skills/{PLUGIN_NAME}")


def build_claude(output: Path, source: Path, version: str) -> None:
    write_json(output / ".claude-plugin/marketplace.json", {
        "name": "naria-skills",
        "owner": {"name": "naria"},
        "plugins": [{
            "name": PLUGIN_NAME,
            "source": f"./plugins/{PLUGIN_NAME}",
            "description": DESCRIPTION,
        }],
    })
    write_json(output / f"plugins/{PLUGIN_NAME}/.claude-plugin/plugin.json", {
        "name": PLUGIN_NAME,
        "version": version,
        "description": DESCRIPTION,
        "author": {"name": "naria"},
        "keywords": ["lecture", "transcript", "pdf", "korean", "study-notes"],
    })
    copy_skill(source, output / f"plugins/{PLUGIN_NAME}/skills/{PLUGIN_NAME}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("openai", "claude"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--repository", required=True)
    args = parser.parse_args()

    source = Path("skills") / PLUGIN_NAME
    if not (source / "SKILL.md").is_file():
        raise SystemExit(f"Canonical skill is missing: {source}")

    output = args.output.resolve()
    remove_generated_contents(output)
    version = f"0.1.0+{args.provider}.{args.source_sha[:12]}"

    if args.provider == "openai":
        build_openai(output, source, version)
    else:
        build_claude(output, source, version)

    write_json(output / "SOURCE.json", {
        "sourceRepository": args.repository,
        "sourceBranch": "main",
        "sourceCommit": args.source_sha,
        "provider": args.provider,
    })


if __name__ == "__main__":
    main()
