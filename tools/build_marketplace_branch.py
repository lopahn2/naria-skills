#!/usr/bin/env python3
"""Build the OpenAI marketplace branch from main/plugins/."""
from __future__ import annotations
import argparse, json, shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CATEGORY, DEVELOPER = "Productivity", "naria"

@dataclass(frozen=True)
class Plugin:
    name: str
    description: str
    skill: Path

def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def discover(root: Path) -> list[Plugin]:
    plugins = []
    for plugin_root in sorted(path for path in root.iterdir() if path.is_dir()):
        manifest_path = plugin_root / ".claude-plugin" / "plugin.json"
        skill = plugin_root / "skills" / plugin_root.name
        skill_md = skill / "SKILL.md"
        if not skill_md.is_file():
            raise ValueError(f"Missing skill: {skill_md}")
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise ValueError(f"Missing Claude plugin manifest: {manifest_path}") from error
        if not isinstance(manifest, dict) or manifest.get("name") != plugin_root.name:
            raise ValueError(f"{manifest_path} name must match {plugin_root.name}")
        description = manifest.get("description")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"{manifest_path} must define a non-empty description")
        plugins.append(Plugin(plugin_root.name, description, skill))
    if not plugins:
        raise ValueError("No plugins found under plugins/")
    return plugins

def openai_manifest(plugin: Plugin, version: str) -> dict[str, Any]:
    return {
        "name": plugin.name,
        "version": version,
        "description": plugin.description,
        "author": {"name": DEVELOPER},
        "skills": "./skills/",
        "interface": {
            "displayName": plugin.name,
            "shortDescription": plugin.description,
            "longDescription": plugin.description,
            "developerName": DEVELOPER,
            "category": CATEGORY,
            "capabilities": [],
            "defaultPrompt": [f"{plugin.name} 스킬을 사용해줘."],
        },
    }

def build(output: Path, plugins: list[Plugin], sha: str) -> None:
    for entry in output.iterdir():
        if entry.name == ".git": continue
        if entry.is_dir(): shutil.rmtree(entry)
        else: entry.unlink()
    write_json(output / ".agents/plugins/marketplace.json", {
        "name": "naria-skills",
        "interface": {"displayName": "Naria Skills"},
        "plugins": [{
            "name": plugin.name,
            "source": {"source": "local", "path": f"./plugins/{plugin.name}"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": CATEGORY,
        } for plugin in plugins],
    })
    for plugin in plugins:
        target = output / "plugins" / plugin.name
        write_json(target / ".codex-plugin/plugin.json", openai_manifest(plugin, f"0.1.0+openai.{sha[:12]}"))
        shutil.copytree(plugin.skill, target / "skills" / plugin.name, copy_function=shutil.copy2)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--repository", required=True)
    args = parser.parse_args()
    plugins, output = discover(Path("plugins")), args.output.resolve()
    build(output, plugins, args.source_sha)
    write_json(output / "SOURCE.json", {
        "sourceRepository": args.repository,
        "sourceBranch": "main",
        "sourceCommit": args.source_sha,
        "provider": "openai",
        "plugins": [plugin.name for plugin in plugins],
    })

if __name__ == "__main__":
    main()
