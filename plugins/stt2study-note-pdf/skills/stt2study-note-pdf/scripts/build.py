#!/usr/bin/env python3
"""파트 HTML 조립 + base64 치환 + PDF 렌더링.

    python3 build.py <out.pdf> <part1.html> <part2.html> ... [--b64 b64.json] [--css template.css]

30쪽 넘는 문서는 한 번에 쓰지 말고 파트로 나눠 쓴 뒤 이걸로 합친다.
이미지는 본문에 {{key}} 플레이스홀더로 두고 여기서 치환한다 —
base64가 본문에 섞이면 이후 편집이 불가능해진다.

파트 파일은 <body> 조각만 담는다. head/style은 이 스크립트가 붙인다.
"""
import sys, os, json, glob, asyncio, re

args = sys.argv[1:]
if not args:
    sys.exit(__doc__)

b64_path, css_path = '/tmp/b64.json', None
parts, out = [], None
i = 0
while i < len(args):
    a = args[i]
    if a == '--b64':   b64_path = args[i + 1]; i += 2; continue
    if a == '--css':   css_path = args[i + 1]; i += 2; continue
    if out is None:    out = a
    else:              parts.append(a)
    i += 1

if css_path is None:
    css_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'template.css')

body = '\n'.join(open(p).read() for p in parts)

b64 = json.load(open(b64_path)) if os.path.exists(b64_path) else {}
for k, v in b64.items():
    body = body.replace('{{' + k + '}}', v)

left = re.findall(r'\{\{(\w+)\}\}', body)
if left:
    sys.exit(f'치환되지 않은 플레이스홀더: {sorted(set(left))}\n'
             f'  → slide.py 로 먼저 추출하거나 {b64_path} 를 확인할 것')

css = open(css_path).read()
html = f'<!DOCTYPE html>\n<html lang="ko"><head><meta charset="utf-8">\n<style>\n{css}\n</style></head><body>\n{body}\n</body></html>'
src = '/tmp/_build.html'
open(src, 'w').write(html)
print(f'조립 완료: {len(parts)}개 파트, {len(html)//1024}KB, 이미지 {len(b64)}개')

from playwright.async_api import async_playwright

async def render():
    exe = sorted(glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome'))
    async with async_playwright() as p:
        b = await p.chromium.launch(**({'executable_path': exe[-1]} if exe else {}))
        pg = await b.new_page()
        await pg.goto(f'file://{src}')
        await pg.wait_for_timeout(900)
        await pg.pdf(path=out, format='A4', print_background=True,
                     margin={'top': '16mm', 'bottom': '15mm', 'left': '15mm', 'right': '15mm'})
        await b.close()

asyncio.run(render())
print(f'렌더 완료: {out}  ({os.path.getsize(out)//1024}KB)')
print('→ verify.py 로 반드시 육안 확인할 것')
