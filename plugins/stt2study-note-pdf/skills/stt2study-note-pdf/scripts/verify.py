#!/usr/bin/env python3
"""렌더 결과 검증 — 컨택트 시트 생성 + 이상 여백 자동 감지.

    python3 verify.py <pdf>

생성된 시트를 Read 툴로 반드시 눈으로 확인한다. 확인 항목:
  · 한글이 깨지거나 누락되지 않았는가
  · SVG 요소가 겹치지 않는가 (특히 화살표와 라벨)
  · 표가 페이지를 가로지르지 않는가
  · 예기치 않은 빈 페이지가 없는가

장(章) 시작 직전 페이지의 하단 여백은 정상이다. 이 스크립트는
그 외의 페이지만 골라 보고한다.
"""
import sys, os, glob, subprocess
import numpy as np
from PIL import Image

pdf = sys.argv[1]
tmp = '/tmp/_vf'
for f in glob.glob(f'{tmp}-*.png'):
    os.remove(f)
subprocess.run(['pdftoppm', '-r', '50', '-png', pdf, tmp], check=True)
pages = sorted(glob.glob(f'{tmp}-*.png'))
print(f'{len(pages)}쪽')

# ── 컨택트 시트 (20쪽씩) ──────────────────────────────────────────
ims = [Image.open(p) for p in pages]
w, h = ims[0].size
cols, per = 10, 20
sheets = []
for s in range(0, len(ims), per):
    chunk = ims[s:s + per]
    rows = (len(chunk) + cols - 1) // cols
    sh = Image.new('RGB', (w * cols, h * rows), 'white')
    for i, im in enumerate(chunk):
        sh.paste(im, ((i % cols) * w, (i // cols) * h))
    path = f'/tmp/sheet{s // per}.png'
    sh.save(path)
    sheets.append(path)
    print(f'  {path}   ({s+1}~{min(s+per,len(ims))}쪽)')

# ── 이상 여백 감지 ────────────────────────────────────────────────
blank = []
for i, p in enumerate(pages):
    a = np.array(Image.open(p).convert('L'))
    ink = (a[int(a.shape[0] * .62):] < 200).mean()
    if ink < 0.004:
        blank.append(i + 1)

if blank:
    print(f'\n하단 여백이 큰 페이지: {blank}')
    print('  장 시작 직전 페이지라면 정상. 그 외라면 figure/table의')
    print('  page-break-inside:avoid 가 원인이니 앞 내용을 조절할 것.')
else:
    print('\n여백 이상 없음')


# ── 콘텐츠 완결성 대조 (노트 vs 최종본) ──────────────────────────
# pdf와 같은 디렉토리가 아니라, 이 스크립트를 실행한 현재 디렉토리(dayNN) 기준으로
# notes/*.md 와 part*.html 을 찾는다. 둘 다 없으면 조용히 건너뛴다(다른 용도로
# verify.py만 따로 돌릴 수도 있으므로 에러로 취급하지 않는다).
import re
import glob as _glob

notes = sorted(_glob.glob('notes/*.md'))
parts = sorted(_glob.glob('part*.html'))

if notes and parts:
    note_text = ''.join(open(f, encoding='utf-8').read() for f in notes)
    part_text = ''.join(open(f, encoding='utf-8').read() for f in parts)

    # 원본 사용(✅) 판정 개수 — "## 교본 도해 판정" 표 안의 ✅ 라인만 세면 더
    # 정확하지만, 그 절만 놓치는 경우보다 과다 카운트가 덜 위험하므로 문서
    # 전체에서 ✅ 개수를 쓴다(과다 카운트는 완결성 경고를 더 자주 띄울 뿐이라
    # 안전한 방향의 오차다).
    approved_diagrams = note_text.count('✅')
    used_images = len(re.findall(r'<img[^>]+src="data:image', part_text))

    # 현장 사례 — "## 현장 사례" 섹션 중 "해당 없음"이 아닌 것만 센다.
    example_sections = re.findall(
        r'## 현장 사례\n(.*?)(?=\n## |\Z)', note_text, re.S
    )
    real_examples = sum(
        1 for sec in example_sections
        if sec.strip() and '해당 없음' not in sec.strip()[:20]
    )
    example_boxes = part_text.count('class="example"')

    print('\n── 콘텐츠 완결성 대조 ──')
    print(f'  원본 도해(✅): 노트 {approved_diagrams}개  vs  최종본 <img> {used_images}개'
          + ('  ⚠ 불일치 — 임의로 SVG 대체했을 가능성, diagram-rules.md 확인'
             if used_images < approved_diagrams else ''))
    print(f'  현장 사례: 노트 {real_examples}개  vs  최종본 .example 박스 {example_boxes}개'
          + ('  ⚠ 불일치 — 사례가 요약/누락됐을 가능성, document-structure.md 확인'
             if example_boxes < real_examples else ''))
    if used_images < approved_diagrams or example_boxes < real_examples:
        print('  → 숫자가 안 맞으면 조용히 넘어가지 말고 사용자에게 먼저 알릴 것'
              ' (PRINCIPLES.md Phase C 참조)')
else:
    print('\n(notes/*.md 또는 part*.html이 현재 디렉토리에 없어 콘텐츠 완결성 대조는 건너뜀)')

print('\n→ 위 시트를 Read 툴로 열어 육안 확인할 것')
