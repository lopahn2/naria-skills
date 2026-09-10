#!/usr/bin/env python3
"""교재 페이지 인덱스에서 '페이지 + 한 줄 요약' 룩업용 jsonl을 뽑는다.

    python3 idx_summary.py <day_dir>

입력:  <day_dir>/idx_<name>.json   prep.py가 만든 페이지 인덱스
출력:  <day_dir>/idx_<name>.summary.jsonl
       한 줄: {"page": N, "title": "...", "one_line": "...", "needs_review": bool}

one_line은 지금은 기계적으로 뽑는다(제목이 있으면 제목, 없으면 본문 앞부분).
kind가 image(텍스트 레이어 부족)이거나 제목이 비어 있으면 needs_review=true로
표시한다 — 그 페이지는 Phase A에서 서브에이전트가 실제로 렌더해서 보고,
더 정확한 내용을 노트(`notes/pMM.md`)에 반영한다.

**이 파일은 최초 페이지 범위 추정 전용 1회성 힌트이며, 그 이후 갱신되지
않는다.** Phase B(통합본 작성)는 이 파일을 읽지 않고 `notes/*.md`와
`cross.jsonl`만 읽으므로, Phase A가 실제로 본 내용이 이 jsonl로 되돌아올
경로 자체가 없다. 갱신 로직(동시쓰기 안전장치 포함)을 추가하는 비용이,
같은 날짜를 부분 재실행할 때만 가끔 발생하는 재탐색 비용보다 크다고 판단해
의도적으로 갱신하지 않는다 — 재탐색이 필요하면 그때 서브에이전트가 다시
찾는다(정상적인 안전망, SKILL.md 참조).

여러 서브에이전트가 동시에 쓰는 파일이 아니라 Phase 0에서 메인이 한 번만
돌리므로 append_cross.py 같은 동시쓰기 안전장치는 필요 없다.
"""
import sys, os, json, glob, re

day = sys.argv[1] if len(sys.argv) > 1 else '.'

def one_line_of(page: dict) -> tuple[str, bool]:
    title = (page.get('title') or '').strip()
    text = (page.get('text') or '').strip()
    if len(title) >= 4:
        return title, False
    if page.get('kind') == 'image':
        return (title or '(이미지 위주 페이지 — 렌더 필요)'), True
    # 텍스트는 있는데 제목이 부실한 경우: 첫 문장 근처에서 자른다
    flat = re.sub(r'\s+', ' ', text)
    snippet = flat[:60].strip()
    return (snippet or '(내용 없음)'), (len(snippet) == 0)

for idx_path in sorted(glob.glob(f'{day}/idx_*.json')):
    if idx_path.endswith('.summary.jsonl'):
        continue
    name = os.path.splitext(os.path.basename(idx_path))[0]
    pages = json.load(open(idx_path, encoding='utf-8'))
    out_path = f'{day}/{name}.summary.jsonl'
    n_review = 0
    with open(out_path, 'w', encoding='utf-8') as f:
        for p in pages:
            one_line, needs_review = one_line_of(p)
            if needs_review:
                n_review += 1
            f.write(json.dumps({
                'page': p['page'],
                'title': p.get('title', ''),
                'one_line': one_line,
                'needs_review': needs_review,
            }, ensure_ascii=False) + '\n')
    print(f'{out_path}: {len(pages)}쪽, 검토 필요 {n_review}쪽 '
          f'(1회성 힌트 — Phase A가 실제로 본 내용은 이 파일에 반영되지 않고 notes/*.md로 감)')
