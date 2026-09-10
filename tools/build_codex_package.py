#!/usr/bin/env python3
"""
Codex는 심볼릭 링크를 못 읽으므로, 스킬 원본(`skills/<name>/`)을
`marketplace/codex/<name>/skills/<name>/`에 그대로(파일로) 복사해 넣는다.

이 스크립트가 만드는 결과물은 빌드 산출물이다 — 절대 손으로 고치지
않는다. 원본을 고치고 이 스크립트를 다시 돌리면 된다. CI(`sync-plugin-version.yml`)가
`skills/**`가 바뀐 push마다 자동으로 이걸 실행하고 달라진 게 있으면 다시 커밋한다.

복사 대상: SKILL.md, PRINCIPLES.md, assets/, references/, scripts/
(README.md, generic-usage.md 등 레포 문서는 패키징 대상이 아니므로 제외)

사용법:
  python3 tools/build_codex_package.py            # 빌드 실행
  python3 tools/build_codex_package.py --check     # 실행 없이 달라진 게 있는지만 확인 (exit 1)
"""
import filecmp
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
MARKETPLACE_CODEX = REPO_ROOT / "marketplace" / "codex"

COPY_ITEMS = ["SKILL.md", "PRINCIPLES.md", "assets", "references", "scripts"]


def dirs_equal(a: Path, b: Path) -> bool:
    if not a.exists() or not b.exists():
        return False
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return False
    for sub in cmp.common_dirs:
        if not dirs_equal(a / sub, b / sub):
            return False
    return True


def main():
    check_only = "--check" in sys.argv
    changed = []

    if not SKILLS_DIR.exists():
        print("skills/ 없음", file=sys.stderr)
        return 2

    for skill_src in sorted(SKILLS_DIR.iterdir()):
        if not skill_src.is_dir():
            continue
        name = skill_src.name
        codex_pkg = MARKETPLACE_CODEX / name
        if not codex_pkg.exists():
            continue  # 이 스킬은 Codex 패키징을 안 함 (marketplace.json에도 없을 것)

        dest = codex_pkg / "skills" / name
        for item in COPY_ITEMS:
            src_item = skill_src / item
            dest_item = dest / item
            if not src_item.exists():
                continue
            if src_item.is_dir():
                same = dirs_equal(src_item, dest_item)
            else:
                same = dest_item.exists() and filecmp.cmp(src_item, dest_item, shallow=False)
            if same:
                continue
            changed.append(f"{name}/{item}")
            if not check_only:
                if dest_item.exists():
                    if dest_item.is_dir():
                        shutil.rmtree(dest_item)
                    else:
                        dest_item.unlink()
                if src_item.is_dir():
                    shutil.copytree(src_item, dest_item)
                else:
                    dest.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_item, dest_item)

    if changed:
        verb = "어긋남 발견" if check_only else "동기화함"
        for c in changed:
            print(f"{verb}: {c}")
        return 1

    print("Codex 패키징이 이미 원본과 동일함")
    return 0


if __name__ == "__main__":
    sys.exit(main())
