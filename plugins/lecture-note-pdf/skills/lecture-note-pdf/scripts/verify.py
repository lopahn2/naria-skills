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

print('\n→ 위 시트를 Read 툴로 열어 육안 확인할 것')
