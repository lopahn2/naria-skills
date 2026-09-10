#!/usr/bin/env python3
"""Build the OpenAI marketplace branch from main/plugins/."""
from __future__ import annotations
import argparse, json, re, shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CATEGORY, DEVELOPER = "Productivity", "naria"
FRONTMATTER = re.compile(r"\A---\s*\n(?P<body>.*?)\n---", re.DOTALL)
FIELD = re.compile(r"^(?P<key>name|description):\s*(?P<value>.+?)\s*$", re.MULTILINE)

@dataclass(frozen=True)
class Plugin:
    name: str
    description: str
    skill: Path
    metadata: dict[str, Any]

def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def discover(root: Path) -> list[Plugin]:
    plugins = []
    for plugin_root in sorted(path for path in root.iterdir() if path.is_dir()):
        skill = plugin_root / "skills" / plugin_root.name
        skill_md = skill / "SKILL.md"
        match = FRONTMATTER.match(skill_md.read_text(encoding="utf-8"))
        if match is None:
            raise ValueError(f"{skill_md} must start with YAML frontmatter")
        fields = {item.group("key"): item.group("value").strip().strip(chr(39) + chr(34)) for item in FIELD.finditer(match.group("body"))}
        if not fields.get("name") or not fields.get("description") or fields["name"] != plugin_root.name:
            raise ValueError(f"{skill_md} name and description must be valid, and name must match {plugin_root.name}")
        metadata = json.loads((plugin_root / "marketplace.json").read_text(encoding="utf-8"))
        if not isinstance(metadata, dict):
            raise ValueError(f"{plugin_root}/marketplace.json must contain a JSON object")
        plugins.append(Plugin(plugin_root.name, fields["description"], skill, metadata))
    if not plugins:
        raise ValueError("No plugins found under plugins/")
    return plugins

def openai_manifest(plugin: Plugin, version: str) -> dict[str, Any]:
    meta = plugin.metadata.get("openai", {})
    if not isinstance(meta, dict):
        raise ValueError(f"{plugin.name}/marketplace.json openai must be an object")
    prompt = meta.get("defaultPrompt", [f"{plugin.name} 스킬을 사용해줘."])
    if isinstance(prompt, str):
        prompt = [prompt]
    if not isinstance(prompt, list) or not all(isinstance(value, str) and value.strip() for value in prompt):
        raise ValueError(f"{plugin.name}/marketplace.json openai.defaultPrompt must be a string or string array")
    display, short = meta.get("displayName", plugin.name), meta.get("shortDescription", plugin.description)
    if not isinstance(display, str) or not display.strip() or not isinstance(short, str) or not short.strip():
        raise ValueError(f"{plugin.name}/marketplace.json must define non-empty OpenAI display fields")
    return {"name": plugin.name, "version": version, "description": plugin.description, "author": {"name": DEVELOPER}, "skills": "./skills/", "interface": {"displayName": display, "shortDescription": short, "longDescription": plugin.description, "developerName": DEVELOPER, "category": meta.get("category", CATEGORY), "capabilities": [], "defaultPrompt": prompt}}

def build(output: Path, plugins: list[Plugin], sha: str) -> None:
    for entry in output.iterdir():
        if entry.name == ".git": continue
        if entry.is_dir(): shutil.rmtree(entry)
        else: entry.unlink()
    write_json(output / ".agents/plugins/marketplace.json", {"name": "naria-skills", "interface": {"displayName": "Naria Skills"}, "plugins": [{"name": p.name, "source": {"source": "local", "path": f"./plugins/{p.name}"}, "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "category": p.metadata.get("openai", {}).get("category", CATEGORY)} for p in plugins]})
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
    write_json(output / "SOURCE.json", {"sourceRepository": args.repository, "sourceBranch": "main", "sourceCommit": args.source_sha, "provider": "openai", "plugins": [plugin.name for plugin in plugins]})

if __name__ == "__main__":
    main()
