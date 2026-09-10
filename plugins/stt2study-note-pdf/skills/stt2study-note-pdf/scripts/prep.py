#!/usr/bin/env python3
"""전처리 — 녹취 인코딩 정규화 + 교재 PDF 페이지 인덱싱 + 등급 판정.

    python3 prep.py <day_dir>

입력:  <day_dir>/audio/*.txt   교시별 녹취 (인코딩 무관)
       <day_dir>/slides/*.pdf 교재 (여러 개 가능)
출력:  audio/*.txt 를 UTF-8로 덮어씀
       <day_dir>/idx_<name>.json  페이지 인덱스
       stdout에 교시 목록과 교본 등급
"""
import sys, os, json, glob, re, subprocess

try:
    import chardet, pdfplumber
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install',
                    'chardet', 'pdfplumber', '--break-system-packages', '-q'], check=True)
    import chardet, pdfplumber

day = sys.argv[1] if len(sys.argv) > 1 else '.'

# ── 0. 한글 폰트 사전 체크 ───────────────────────────────────────────
# build.py(Phase C)가 렌더링에 쓰는 template.css는
# font-family: "Noto Sans CJK KR", sans-serif 를 쓴다. 이 폰트가 없으면
# 폴백 sans-serif에 한글 글리프가 없어 PDF 전체가 빈 박스(tofu)로 나올
# 수 있는데, 지금까지는 Phase C 육안 검증에서야 발견됐다 — 그 시점엔
# 서브에이전트 분석(Phase A)과 파트 작성(Phase B)이 이미 다 끝난 뒤라
# 비용이 크다. 비용이 큰 단계 전에 여기서 미리 잡는다.
try:
    out = subprocess.run(['fc-list', ':lang=ko'], capture_output=True, text=True, check=True).stdout
except FileNotFoundError:
    sys.exit('fontconfig(fc-list)가 설치되어 있지 않다. '
             '`apt-get install -y fontconfig fonts-noto-cjk` 후 다시 실행할 것.')

if 'Noto Sans CJK KR' not in out and 'NotoSansCJK' not in out:
    sys.exit('한글 폰트(Noto Sans CJK KR)가 없다 — 이대로 진행하면 PDF에서 '
              '한글이 전부 빈 박스로 나온다.\n'
              '  → `apt-get install -y fonts-noto-cjk` 로 설치 후 다시 실행할 것.\n'
              '  → (fc-list :lang=ko 로 확인 가능한 한글 폰트가 하나도 없음)')

print(f'=== 폰트 ===\n  한글 폰트 확인됨 (fc-list :lang=ko 결과 {len(out.splitlines())}줄)')

# ── 1. 녹취 인코딩 정규화 ────────────────────────────────────────────
print('=== 녹취 ===')
for f in sorted(glob.glob(f'{day}/audio/*.txt')):
    raw = open(f, 'rb').read()
    enc = chardet.detect(raw)['encoding'] or 'utf-8'
    txt = raw.decode(enc, errors='replace').lstrip('﻿')
    open(f, 'w', encoding='utf-8').write(txt)
    ts = re.findall(r'(\d{1,2}:\d{2})', txt)
    print(f'  {os.path.basename(f):<10} {enc:<12} {len(txt):>7,}자  길이 {ts[-1] if ts else "?"}')

# ── 2. 교재 인덱싱 + 등급 판정 ───────────────────────────────────────
print('\n=== 교재 ===')
for pdf in sorted(glob.glob(f'{day}/slides/*.pdf')):
    name = os.path.splitext(os.path.basename(pdf))[0]
    pages = []
    with pdfplumber.open(pdf) as doc:
        for i, pg in enumerate(doc.pages):
            t = (pg.extract_text() or '').strip()
            lines = [l for l in t.split('\n') if l.strip()]
            pages.append({
                'page': i + 1,
                'title': lines[0] if lines else '',
                'text': t,
                'nchars': len(t),
                'nimg': len(pg.images),
                'kind': 'image' if len(t) < 40 else 'text',
            })
    json.dump(pages, open(f'{day}/idx_{name}.json', 'w'), ensure_ascii=False)
    n_img = sum(1 for p in pages if p['kind'] == 'image')
    ratio = n_img / len(pages)
    tier = 'A (텍스트 레이어 충분)' if ratio < .5 else \
           ('B (혼재 — OCR 보강)' if ratio < .9 else 'C (OCR 필요, 비용 증가)')
    print(f'  {name:<20} {len(pages):>4}쪽  이미지쪽 {ratio:>4.0%}  → 등급 {tier}')

    # 섹션 구분 페이지 — 구간 매칭의 안전망
    secs = [p for p in pages if 0 < len(p['text'].strip()) < 25 and p['nimg'] == 0]
    if secs:
        print(f'    섹션 구분 페이지 {len(secs)}개:')
        for p in secs[:20]:
            print(f'      p{p["page"]:>3}  {p["text"].strip()}')
