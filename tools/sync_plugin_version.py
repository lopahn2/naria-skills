#!/usr/bin/env python3
"""
여러 벤더(plugin.json)에 흩어진 버전을 하나로 동기화한다.

이 저장소는 같은 스킬(stt2study-note-pdf)을 벤더별로 별도 plugin.json으로
패키징한다 (Claude / Codex 심볼릭 링크판 / Codex 플랫 복사판). 각자 다른
도구(사람, Claude Code, Codex 자동화)가 독립적으로 버전을 올릴 수 있어서
방치하면 서로 어긋난다.

동작:
1. 아래 PLUGIN_JSON_PATHS 에 명시된 plugin.json들을 읽는다.
2. 각 파일의 "version"에서 base semver(빌드 메타데이터 `+...` 제외)를 뽑아
   그중 가장 높은 것을 "정답"으로 정한다.
3. 모든 파일의 base semver를 그 값으로 맞춘다. 원래 그 파일에
   `+codex.<timestamp>` 같은 빌드 메타데이터가 붙어있었다면, 형식은
   유지하되 타임스탬프만 지금 시각으로 새로 찍는다.
4. 변경이 있었으면 어떤 파일을 어떻게 고쳤는지 stdout에 출력하고
   exit code 1을 반환한다 (CI에서 "동기화가 필요했다"는 신호로 쓸 수 있음).
   변경이 없었으면 조용히 exit code 0.

사용법:
  python3 tools/sync_plugin_version.py            # 동기화 실행
  python3 tools/sync_plugin_version.py --check     # 실행하지 않고 어긋남만 검사 (CI용)
"""
import json
import re
import sys
import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# 동기화 대상 plugin.json 목록. 벤더가 늘어나면 여기에 경로만 추가하면 된다.
PLUGIN_JSON_PATHS = [
    REPO_ROOT / "skills/stt2study-note-pdf/vendors/claude/.claude-plugin/plugin.json",
    REPO_ROOT / "skills/stt2study-note-pdf/vendors/openai/.codex-plugin/plugin.json",
    REPO_ROOT / "plugins/stt2study-note-pdf/.codex-plugin/plugin.json",
]

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)")


def parse_base(version: str):
    m = SEMVER_RE.match(version)
    if not m:
        raise ValueError(f"semver로 파싱할 수 없는 버전: {version!r}")
    return tuple(int(x) for x in m.groups())


def build_suffix(version: str) -> str:
    """'+codex.20260910030449' 같은 빌드 메타데이터 부분만 뽑는다 (없으면 빈 문자열)."""
    if "+" in version:
        return version.split("+", 1)[1]
    return ""


def main():
    check_only = "--check" in sys.argv

    entries = []
    for path in PLUGIN_JSON_PATHS:
        if not path.exists():
            print(f"경고: {path} 없음, 건너뜀", file=sys.stderr)
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        version = data.get("version", "")
        entries.append({"path": path, "data": data, "version": version})

    if not entries:
        print("동기화할 plugin.json을 하나도 못 찾음", file=sys.stderr)
        return 2

    highest = max(parse_base(e["version"]) for e in entries)
    highest_str = ".".join(str(x) for x in highest)

    changed = []
    for e in entries:
        current_base = parse_base(e["version"])
        if current_base == highest:
            continue
        suffix = build_suffix(e["version"])
        if suffix.startswith("codex."):
            ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S")
            new_version = f"{highest_str}+codex.{ts}"
        else:
            new_version = highest_str
        changed.append((e["path"], e["version"], new_version))
        if not check_only:
            e["data"]["version"] = new_version
            e["path"].write_text(
                json.dumps(e["data"], ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    if changed:
        verb = "어긋남 발견" if check_only else "동기화함"
        for path, old, new in changed:
            rel = path.relative_to(REPO_ROOT)
            print(f"{verb}: {rel}  {old} -> {new}")
        return 1

    print(f"이미 모두 {highest_str}로 동기화되어 있음")
    return 0


if __name__ == "__main__":
    sys.exit(main())
