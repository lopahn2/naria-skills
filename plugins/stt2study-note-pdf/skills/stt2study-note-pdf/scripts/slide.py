#!/usr/bin/env python3
"""교재 원본 도해를 잘라 base64로 뽑는다.

    python3 slide.py <pdf> <page> <key> [crop_l,t,r,b] [--out b64.json]
    python3 slide.py <pdf> <page> --view          # 눈으로 확인만 (PNG 경로 출력)

원본이 이미 도해면 다시 그리지 말고 이걸로 가져다 쓴다.
표현하는 축이 2개 이상인 그림을 다시 그리면 반드시 축을 잃는다.

**기본은 crop 인자 없이 페이지 전체를 그대로 쓰는 것이다** (여백만 자동 제거).
crop 좌표는 한 페이지에 무관한 도해가 여럿 섞여 반드시 분리해야 할 때만 쓴다 —
눈대중 좌표가 어긋나면 최종본에서 그림이 잘리거나 깨지는 사고로 이어진다.
crop을 쓸 때는 --view 로 먼저 픽셀 크기를 확인하고, 결과를 verify.py 컨택트
시트로 반드시 다시 육안 확인할 것. 자세한 사유는
references/diagram-rules.md 참고.

pdf 경로가 `dayNN/slides/...` 형태면 크롭 좌표를 `dayNN/diagrams.json` 에도
같이 기록한다 — 나중에 노트(②)와 원본 교재(③)만 가지고 똑같은 도해를 다시
잘라낼 때, 좌표를 눈대중으로 다시 잡지 않아도 되게 하기 위해서다.
b64.json은 렌더링 캐시(작업용, ④)라 재현에 쓰지 않는다.
"""
import sys, os, re, json, glob, io, base64, subprocess, tempfile
from PIL import Image, ImageChops


def find_day_dir(pdf_path: str):
    """dayNN/slides/x.pdf → dayNN. 패턴이 아니면 None."""
    m = re.search(r"(.*?/)?(?P<day>[^/]+)/slides/[^/]+\.pdf$", pdf_path.replace("\\", "/"))
    return m.group("day") if m else None


def record_crop(pdf, page, key, crop):
    day = find_day_dir(pdf)
    if not day:
        return  # dayNN/slides/ 규칙을 안 따르면 기록할 곳을 특정 못 함 — 조용히 넘어감
    log_path = os.path.join(day, "diagrams.json")
    records = json.load(open(log_path)) if os.path.exists(log_path) else []
    records = [r for r in records if r.get("key") != key]  # 재실행 시 갱신
    records.append({
        "key": key,
        "source_pdf": os.path.basename(pdf),
        "page": page,
        "crop": list(crop) if crop else "auto",
    })
    json.dump(records, open(log_path, "w"), ensure_ascii=False, indent=0)

if len(sys.argv) < 3:
    sys.exit(__doc__)
pdf, page = sys.argv[1], int(sys.argv[2])
dpi = 150

# 호출마다 격리된 임시 디렉터리를 쓴다. 이전에는 고정 접두사(/tmp/_sl-*)를
# 재사용해 여러 번 호출하면 이전 페이지(심지어 이전 세션의 다른 PDF) 결과가
# 남아 있었고, glob으로 "가장 마지막 파일"을 집어오다 보니 페이지 번호가
# 두 자리를 넘거나 이전 실행 잔재가 있으면 완전히 엉뚱한 이미지를 골라오는
# 사고가 났다(예: 51쪽 잔재가 07~38쪽 요청에 전부 끼어듦). 매 호출을 별도
# 디렉터리에서 실행하면 그 안엔 방금 만든 파일 하나뿐이라 이 문제가 원천적으로
# 사라진다.
tmpdir = tempfile.mkdtemp(prefix='lecture_slide_')
subprocess.run(['pdftoppm', '-f', str(page), '-l', str(page), '-r', str(dpi),
                '-png', pdf, os.path.join(tmpdir, 'pg')], check=True)
matches = glob.glob(os.path.join(tmpdir, 'pg-*.png'))
if len(matches) != 1:
    sys.exit(f'페이지 {page} 렌더링 실패 또는 예상 밖 출력 개수: {matches}')
src = matches[0]

if '--view' in sys.argv:
    im = Image.open(src)
    print(f'{src}   크기 {im.size[0]}x{im.size[1]}  (crop 좌표는 이 픽셀 기준)')
    sys.exit()

key = sys.argv[3]
crop = None
for a in sys.argv[4:]:
    if ',' in a:
        crop = tuple(int(x) for x in a.split(','))

if crop:
    print('주의: crop 좌표 지정됨 — 눈대중 좌표가 어긋나면 그림이 잘리거나 깨질 '
          '수 있다. 무관한 도해가 섞여 분리해야 하는 경우가 아니라면 crop 없이 '
          '페이지 전체를 쓰는 것을 권장한다 (references/diagram-rules.md 참고). '
          'crop 결과는 verify.py 컨택트 시트로 반드시 재확인할 것.', file=sys.stderr)

im = Image.open(src).convert('RGB')
if crop:
    im = im.crop(crop)
else:                                   # 여백 자동 제거
    bb = ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).getbbox()
    im = im.crop(bb)
im.thumbnail((1250, 1250))

buf = io.BytesIO()
im.save(buf, 'PNG', optimize=True)
b64 = base64.b64encode(buf.getvalue()).decode()

out = '/tmp/b64.json'
for a in sys.argv:
    if a.startswith('--out'):
        out = sys.argv[sys.argv.index(a) + 1]
store = json.load(open(out)) if os.path.exists(out) else {}
store[key] = b64
json.dump(store, open(out, 'w'))

record_crop(pdf, page, key, crop)

print(f'{key}: {im.size[0]}x{im.size[1]}  {len(buf.getvalue())//1024}KB  → {out}')
print(f'본문에서 <img src="data:image/png;base64,{{{{{key}}}}}"> 로 참조')
