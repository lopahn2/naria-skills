#!/usr/bin/env python3
"""Build provider marketplace branches from canonical skills/ directories."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_CATEGORY = "Productivity"
DEFAULT_DEVELOPER = "naria"
FRONTMATTER = re.compile(r"\A---\s*\n(?P<body>.*?)\n---", re.DOTALL)
FRONTMATTER_FIELD = re.compile(r"^(?P<key>name|description):\s*(?P<value>.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    source: Path
    metadata: dict[str, Any]


def remove_generated_contents(root: Path) -> None:
    for entry in root.iterdir():
        if entry.name == ".git":
            continue
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_frontmatter(skill_md: Path) -> dict[str, str]:
    contents = skill_md.read_text(encoding="utf-8")
    match = FRONTMATTER.match(contents)
    if match is None:
        raise ValueError(f"{skill_md} must start with YAML frontmatter")
    fields = {item.group("key"): item.group("value").strip().strip("'\"") for item in FRONTMATTER_FIELD.finditer(match.group("body"))}
    if not fields.get("name") or not fields.get("description"):
        raise ValueError(f"{skill_md} must define non-empty name and description")
    return fields


def read_metadata(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"Missing required marketplace metadata: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON: {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def discover_skills(skills_root: Path) -> list[Skill]:
    skills: list[Skill] = []
    seen_names: set[str] = set()

    for source in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        skill_md = source / "SKILL.md"
        if not skill_md.is_file():
            continue

        fields = read_frontmatter(skill_md)
        name = fields["name"]
        if name != source.name:
            raise ValueError(f"Skill name must match directory: {source.name} != {name}")
        if name in seen_names:
            raise ValueError(f"Duplicate skill name: {name}")
        seen_names.add(name)

        skills.append(Skill(
            name=name,
            description=fields["description"],
            source=source,
            metadata=read_metadata(source / "marketplace.json"),
        ))

    if not skills:
        raise ValueError("No canonical skills found under skills/")
    return skills


def copy_skill(skill: Skill, output: Path) -> None:
    shutil.copytree(skill.source, output / f"plugins/{skill.name}/skills/{skill.name}", copy_function=shutil.copy2)


def openai_plugin(skill: Skill, version: str) -> dict[str, Any]:
    metadata = skill.metadata.get("openai", {})
    if not isinstance(metadata, dict):
        raise ValueError(f"{skill.source}/marketplace.json openai must be an object")

    prompt = metadata.get("defaultPrompt", [f"{skill.name} 스킬을 사용해줘."])
    if isinstance(prompt, str):
        prompt = [prompt]
    if not isinstance(prompt, list) or not all(isinstance(item, str) and item.strip() for item in prompt):
        raise ValueError(f"{skill.source}/marketplace.json openai.defaultPrompt must be a string or string array")

    display_name = metadata.get("displayName", skill.name)
    short_description = metadata.get("shortDescription", skill.description)
    if not isinstance(display_name, str) or not display_name.strip():
        raise ValueError(f"{skill.source}/marketplace.json openai.displayName must be a non-empty string")
    if not isinstance(short_description, str) or not short_description.strip():
        raise ValueError(f"{skill.source}/marketplace.json openai.shortDescription must be a non-empty string")

    return {
        "name": skill.name,
        "version": version,
        "description": skill.description,
        "author": {"name": DEFAULT_DEVELOPER},
        "skills": "./skills/",
        "interface": {
            "displayName": display_name,
            "shortDescription": short_description,
            "longDescription": skill.description,
            "developerName": DEFAULT_DEVELOPER,
            "category": metadata.get("category", DEFAULT_CATEGORY),
            "capabilities": [],
            "defaultPrompt": prompt,
        },
    }


def claude_plugin(skill: Skill, version: str) -> dict[str, Any]:
    metadata = skill.metadata.get("claude", {})
    if not isinstance(metadata, dict):
        raise ValueError(f"{skill.source}/marketplace.json claude must be an object")
    keywords = metadata.get("keywords", [])
    if not isinstance(keywords, list) or not all(isinstance(item, str) and item.strip() for item in keywords):
        raise ValueError(f"{skill.source}/marketplace.json claude.keywords must be a string array")

    return {
        "name": skill.name,
        "version": version,
        "description": skill.description,
        "author": {"name": DEFAULT_DEVELOPER},
        "keywords": keywords,
    }


def build_openai(output: Path, skills: list[Skill], source_sha: str) -> None:
    write_json(output / ".agents/plugins/marketplace.json", {
        "name": "naria-skills",
        "interface": {"displayName": "Naria Skills"},
        "plugins": [{
            "name": skill.name,
            "source": {"source": "local", "path": f"./plugins/{skill.name}"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": skill.metadata.get("openai", {}).get("category", DEFAULT_CATEGORY),
        } for skill in skills],
    })

    for skill in skills:
        version = f"0.1.0+openai.{source_sha[:12]}"
        write_json(output / f"plugins/{skill.name}/.codex-plugin/plugin.json", openai_plugin(skill, version))
        copy_skill(skill, output)


def build_claude(output: Path, skills: list[Skill], source_sha: str) -> None:
    write_json(output / ".claude-plugin/marketplace.json", {
        "name": "naria-skills",
        "owner": {"name": DEFAULT_DEVELOPER},
        "plugins": [{
            "name": skill.name,
            "source": f"./plugins/{skill.name}",
            "description": skill.description,
        } for skill in skills],
    })

    for skill in skills:
        version = f"0.1.0+claude.{source_sha[:12]}"
        write_json(output / f"plugins/{skill.name}/.claude-plugin/plugin.json", claude_plugin(skill, version))
        copy_skill(skill, output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("openai", "claude"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--repository", required=True)
    args = parser.parse_args()

    skills = discover_skills(Path("skills"))
    output = args.output.resolve()
    remove_generated_contents(output)

    if args.provider == "openai":
        build_openai(output, skills, args.source_sha)
    else:
        build_claude(output, skills, args.source_sha)

    write_json(output / "SOURCE.json", {
        "sourceRepository": args.repository,
        "sourceBranch": "main",
        "sourceCommit": args.source_sha,
        "provider": args.provider,
        "skills": [skill.name for skill in skills],
    })


if __name__ == "__main__":
    main()
