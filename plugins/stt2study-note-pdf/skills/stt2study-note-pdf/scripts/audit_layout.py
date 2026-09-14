#!/usr/bin/env python3
"""파트 HTML의 겹침·화살표 위험 요소를 렌더 전 차단한다.

    python3 audit_layout.py part1.html [part2.html ...]

시각 검수(verify.py)를 대신하지 않는다. 문단 안의 블록 박스, 본문 위에 뜨는
위치 지정, 여러 연결을 한 path에 묶은 marker-end처럼 반복된 구조적 실수를 먼저 막는다.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


TAG = re.compile(r"<(?P<name>[A-Za-z][\w:-]*)\b(?P<attrs>[^>]*)>", re.S)
CLASS = re.compile(r"\bclass\s*=\s*(['\"])(?P<value>.*?)\1", re.S | re.I)
STYLE = re.compile(r"\bstyle\s*=\s*(['\"])(?P<value>.*?)\1", re.S | re.I)
PATH = re.compile(r"<path\b(?P<attrs>[^>]*)>", re.S | re.I)
ATTR = re.compile(r"\b(?P<name>[\w:-]+)\s*=\s*(['\"])(?P<value>.*?)\2", re.S | re.I)


def attrs_map(attrs: str) -> dict[str, str]:
    return {m.group('name').lower(): m.group('value') for m in ATTR.finditer(attrs)}


def audit(path: Path) -> list[str]:
    text = path.read_text(encoding='utf-8')
    errors: list[str] = []
    for match in TAG.finditer(text):
        name, attrs = match.group('name').lower(), match.group('attrs')
        class_match = CLASS.search(attrs)
        classes = set(class_match.group('value').split()) if class_match else set()
        if 'key' in classes and name != 'div':
            errors.append(f'{path}: .key는 <div> 블록으로만 써야 함 (<{name}>)')
        style_match = STYLE.search(attrs)
        if style_match and re.search(r'position\s*:\s*(absolute|fixed)', style_match.group('value'), re.I):
            errors.append(f'{path}: 본문 요소에 position:absolute|fixed 사용 금지')
        if style_match and re.search(r'(margin-(?:top|right|bottom|left)|margin)\s*:\s*-', style_match.group('value'), re.I):
            errors.append(f'{path}: 본문 요소에 음수 margin 사용 금지')
        if style_match and re.search(r'transform\s*:', style_match.group('value'), re.I):
            errors.append(f'{path}: 본문 요소에 transform 사용 금지')

    for match in PATH.finditer(text):
        attrs = attrs_map(match.group('attrs'))
        d = attrs.get('d', '')
        has_marker = any(key in attrs for key in ('marker-end', 'marker-start', 'marker-mid'))
        if has_marker and len(re.findall(r'[Mm]', d)) > 1:
            errors.append(f'{path}: marker가 있는 <path>는 연결 하나만 포함해야 함')
    return errors


def main() -> None:
    files = [Path(arg) for arg in sys.argv[1:]]
    if not files:
        raise SystemExit(__doc__)
    errors = [error for path in files for error in audit(path)]
    if errors:
        raise SystemExit('레이아웃 사전 검사 실패:\n  - ' + '\n  - '.join(errors))
    print(f'레이아웃 사전 검사 통과: {len(files)}개 파트')


if __name__ == '__main__':
    main()
