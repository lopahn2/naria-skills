#!/usr/bin/env python3
"""
dayNN 의 중간 산출물(②)과 입력 자료(③)를 OKF(Open Knowledge Format) 문서로
감싸 ./okf/dayNN/ 에 만든다. 최종 통합본(①)과 작업용 임시 파일(④)은 대상이 아니다.

    python3 build_okf.py <project> <dayNN>

- 마크다운 산출물(notes/pMM.md)은 내용을 그대로 복사하고 OKF 프론트매터만 얹는다.
- 마크다운이 아닌 산출물(audio/*.txt, slides/*.pdf, idx_*.json, cross.jsonl,
  diagrams.json)은 포인터 문서를 만든다 — 내용을 재작성하지 않고
  `resource:` 필드로 원본 경로만 가리킨다.
- 프로젝트 루트 누적 파일(glossary.md)은 okf/glossary.md 로 미러링한다(day 무관).
- okf/index.md 는 전체를 다시 스캔해 매번 재생성한다(멱등).
- okf/log.md 는 이번 실행 결과를 한 줄 append한다.

`project`는 로컬 폴더명이 아니라 **사람이 붙인 프로젝트 이름**이다(예: ax-advanced).
이 이름은 모든 OKF 문서의 frontmatter에 `project:` 로 박히는데, 나중에 여러
강의(프로젝트)의 okf/ 트리를 한 지식베이스에 합쳐도 어느 프로젝트 소속인지
구분하기 위해서다. OpenViking처럼 프로젝트 단위 네임스페이스가 있는 곳에
업로드할 때는 이 이름을 그대로 쓰되, **원격에 같은 이름의 프로젝트가 없으면
새로 만들기 전에 사용자에게 이 이름이 맞는지 반드시 확인한다** — 이건 이
스크립트가 하는 일이 아니라 업로드를 실행하는 에이전트가 지켜야 할 규칙이다
(references/okf-spec.md 참조).
"""
import sys
import json
import re
import glob
import os
from datetime import datetime, timezone
from pathlib import Path

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fm(**fields):
    """OKF 프론트매터를 만든다. None/빈 값은 뺀다."""
    lines = ["---"]
    for k, v in fields.items():
        if v is None or v == "" or v == []:
            continue
        if isinstance(v, list):
            items = ", ".join(json.dumps(x, ensure_ascii=False) for x in v)
            lines.append(f"{k}: [{items}]")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        else:
            s = str(v).replace('"', '\\"')
            lines.append(f'{k}: "{s}"')
    lines.append("---\n")
    return "\n".join(lines)


def write_doc(path: Path, frontmatter: str, body: str = ""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(frontmatter + body, encoding="utf-8")
    return path


def extract_note_meta(md_text: str):
    """notes/pMM.md 에서 title/one_line/tags를 뽑는다. 실패해도 빈 값으로 넘어간다."""
    title_m = re.search(r"^#\s*(.+)$", md_text, re.M)
    title = title_m.group(1).strip() if title_m else ""

    one_line_m = re.search(r"##\s*한\s*문장\s*\n+(.+)", md_text)
    one_line = one_line_m.group(1).strip() if one_line_m else ""

    tech_block_m = re.search(r"##\s*언급\s*기술.*?\n((?:\|.*\n)+)", md_text)
    tags = []
    if tech_block_m:
        rows = tech_block_m.group(1).strip().split("\n")[2:]  # 헤더/구분선 제외
        for r in rows:
            cells = [c.strip() for c in r.strip("|").split("|")]
            if cells and cells[0] and cells[0] not in ("이름",):
                tags.append(cells[0])
    return title, one_line, tags[:12]


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: build_okf.py <project> <dayNN>")
    project, day = sys.argv[1], sys.argv[2]
    day_dir = Path(day)
    if not day_dir.exists():
        sys.exit(f"error: {day_dir} 없음")

    okf_root = Path("okf")
    okf_day = okf_root / day
    made = []

    # ── notes/pMM.md → 내용 복사 + 프론트매터 ─────────────────────────
    for note in sorted(day_dir.glob("notes/*.md")):
        if note.name.endswith(".cross.json"):
            continue
        text = note.read_text(encoding="utf-8")
        title, one_line, tags = extract_note_meta(text)
        out = okf_day / "notes" / note.name
        header = fm(
            type="lecture-note",
            project=project,
            title=title or note.stem,
            description=one_line,
            tags=tags + [day],
            timestamp=NOW,
        )
        write_doc(out, header, text)
        made.append(out)

    # ── audio/*.txt → 포인터 ──────────────────────────────────────────
    for f in sorted(day_dir.glob("audio/*.txt")):
        out = okf_day / "sources" / f"{f.stem}-audio.md"
        header = fm(
            type="source-transcript",
            project=project,
            title=f"{f.stem} 원본 녹취",
            description="STT 원문 (UTF-8 정규화됨). 노트 작성의 정본.",
            resource=str(f),
            tags=[day, "transcript"],
            timestamp=NOW,
        )
        write_doc(out, header)
        made.append(out)

    # ── slides/*.pdf → 포인터 ─────────────────────────────────────────
    for f in sorted(day_dir.glob("slides/*.pdf")):
        out = okf_day / "sources" / f"{f.stem}-textbook.md"
        header = fm(
            type="source-textbook",
            project=project,
            title=f"{f.stem} 교재",
            description="원본 교재 PDF.",
            resource=str(f),
            tags=[day, "textbook"],
            timestamp=NOW,
        )
        write_doc(out, header)
        made.append(out)

    # ── idx_<name>.json → 포인터 ──────────────────────────────────────
    for f in sorted(day_dir.glob("idx_*.json")):
        name = f.stem[len("idx_"):]
        out = okf_day / "sources" / f"idx-{name}.md"
        header = fm(
            type="textbook-index",
            project=project,
            title=f"{name} 페이지 인덱스",
            description="교재 페이지별 제목/텍스트/이미지여부/등급 (prep.py 출력).",
            resource=str(f),
            tags=[day, "index"],
            timestamp=NOW,
        )
        write_doc(out, header)
        made.append(out)

    # ── cross.jsonl → 포인터 ──────────────────────────────────────────
    cross = day_dir / "cross.jsonl"
    if cross.exists():
        n = sum(1 for _ in cross.open(encoding="utf-8") if _.strip())
        out = okf_day / "cross.md"
        header = fm(
            type="cross-index",
            project=project,
            title=f"{day} 교차 후보 인덱스",
            description=f"교시별 한 문장 + 교차 후보 {n}건. 여러 날짜 취합 시 이것부터 본다.",
            resource=str(cross),
            tags=[day, "cross-index"],
            timestamp=NOW,
        )
        write_doc(out, header)
        made.append(out)

    # ── diagrams.json → 포인터 (있으면) ────────────────────────────────
    diagrams = day_dir / "diagrams.json"
    if diagrams.exists():
        out = okf_day / "diagrams.md"
        header = fm(
            type="diagram-crop-log",
            project=project,
            title=f"{day} 도해 크롭 기록",
            description="원본 슬라이드에서 잘라 쓴 도해의 페이지·크롭 좌표. "
                        "재현 시 같은 도해를 다시 눈대중으로 자르지 않기 위한 기록.",
            resource=str(diagrams),
            tags=[day, "diagrams"],
            timestamp=NOW,
        )
        write_doc(out, header)
        made.append(out)

    # ── glossary.md (프로젝트 전체 누적, day 무관) → okf/glossary.md 미러 ──
    glossary = Path("glossary.md")
    if glossary.exists():
        text = glossary.read_text(encoding="utf-8")
        out = okf_root / "glossary.md"
        header = fm(
            type="glossary",
            project=project,
            title=f"{project} 누적 기술 용어집",
            description="전 과정 누적 기술 용어집. 회차가 쌓일수록 갱신됨.",
            tags=["glossary"],
            timestamp=NOW,
        )
        write_doc(out, header, text)
        made.append(out)

    # ── index.md 전체 재생성 (멱등) ─────────────────────────────────────
    days = sorted(p.name for p in okf_root.glob("day*") if p.is_dir())
    idx_lines = [f'---\ntype: "index"\nproject: "{project}"\ntitle: "{project} OKF 색인"\ntimestamp: "{NOW}"\n---\n']
    idx_lines.append(f"# {project} — 지식 색인\n")
    for d in days:
        idx_lines.append(f"\n## {d}\n")
        for sub in sorted((okf_root / d).rglob("*.md")):
            rel = sub.relative_to(okf_root)
            idx_lines.append(f"- [{sub.stem}](/{rel})")
    if (okf_root / "glossary.md").exists():
        idx_lines.append("\n## 용어집\n")
        idx_lines.append("- [glossary](/glossary.md)")
    (okf_root / "index.md").write_text("\n".join(idx_lines) + "\n", encoding="utf-8")

    # ── log.md append ───────────────────────────────────────────────────
    log_path = okf_root / "log.md"
    log_line = f"- {NOW} · {day} · 문서 {len(made)}개 추가/갱신\n"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(log_line)

    print(f"okf/{day}/ 에 {len(made)}개 OKF 문서 생성, index.md/log.md 갱신")
    for p in made:
        print(f"  {p}")


if __name__ == "__main__":
    main()
