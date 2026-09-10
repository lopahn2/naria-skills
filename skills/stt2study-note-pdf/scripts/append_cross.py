#!/usr/bin/env python3
"""
서브에이전트가 자기 교시의 "한 문장 + 교차 후보"를 dayNN/cross.jsonl 에
한 줄 append한다. 파일이 없으면 만든다.

여러 서브에이전트가 동시에 이 스크립트를 호출해도 안전하다 — 한 줄(보통
수백 바이트)을 append 모드로 **한 번의 write() 호출**로 쓰기 때문에,
리눅스 로컬 파일시스템에서는 PIPE_BUF(4096바이트) 이내 쓰기가 인터리빙되지
않는다. 그래서 별도의 잠금이나 병합 단계 없이 그냥 밀어넣기만 하면 된다.

사용 (stdin으로 JSON 한 덩어리를 준다):
    echo '{"chapter":"p03","title":"OKF와 문서 표준",
           "one_line":"...",
           "cross":["프론트매터 필터링: 5교시 복선", "..."]}' \
      | python3 append_cross.py dayNN

메인 에이전트가 여러 날짜를 취합할 때는 이 파일을 쓰지 않고 **읽기만** 한다:
    for f in day*/cross.jsonl; do cat "$f"; done
"""
import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("usage: append_cross.py dayNN  (JSON을 stdin으로)", file=sys.stderr)
        sys.exit(1)

    day_dir = Path(sys.argv[1])
    day_dir.mkdir(parents=True, exist_ok=True)

    raw = sys.stdin.read()
    rec = json.loads(raw)
    rec.setdefault("day", day_dir.name)
    if "chapter" not in rec or "one_line" not in rec:
        print("error: chapter, one_line 은 필수", file=sys.stderr)
        sys.exit(1)
    rec.setdefault("cross", [])

    line = json.dumps(rec, ensure_ascii=False)
    encoded = line.encode("utf-8")
    if len(encoded) > 3000:
        print(
            f"경고: {rec['chapter']} 한 줄이 {len(encoded)}바이트 — "
            "요약이 아니라 본문 수준을 옮겨쓴 건 아닌지 확인",
            file=sys.stderr,
        )

    path = day_dir / "cross.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

    print(f"{path} ← {rec['chapter']} 추가 ({len(encoded)}바이트)")


if __name__ == "__main__":
    main()
