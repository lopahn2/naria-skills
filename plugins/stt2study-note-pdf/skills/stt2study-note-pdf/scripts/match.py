#!/usr/bin/env python3
"""교시 × 교본 매칭 행렬 — 어느 교시가 어느 교본에 대응하는지 판정.

    python3 match.py <day_dir> [추가,기술어,쉼표구분]

기능어 빈도 대조는 쓰지 않는다. 구어체 녹취는 상위어가 전부
"이제/그래서/근데"라 변별력이 없다. 기술어 사전 기반으로 판정한다.

판정 기준:
  70% 이상  → 대응 교본 확실
  30~70%    → 약한 대응. 참고로만
  30% 미만  → 교재 없이 진행된 교시 (정상)
  전 교시가 전부 낮음 → 자료 자체가 틀렸을 가능성. 사용자에게 확인.
"""
import sys, os, json, glob, re

day = sys.argv[1] if len(sys.argv) > 1 else '.'

TERMS = """하네스 스킬 컨텍스트 프롬프트 에이전트 벡터 임베딩 청크 검색 시멘틱 키워드
그래프 노드 평가 도구 랭체인 LangGraph LangChain RAG 메타 목차 피드백 지식 온톨로지
리트리버 리랭커 토큰 캐싱 라우터 MCP ReAct 리액트 파인튜닝 할루시네이션 트레이싱
아키텍처 파이프라인 프레임워크 데이터셋 벤치마크 인덱싱 클러스터링 워크플로우""".split()
if len(sys.argv) > 2:
    TERMS += [t.strip() for t in sys.argv[2].split(',') if t.strip()]

idx = {os.path.basename(f)[4:-5]: json.load(open(f))
       for f in sorted(glob.glob(f'{day}/idx_*.json'))}
if not idx:
    sys.exit('idx_*.json 이 없다. prep.py 를 먼저 실행할 것.')
books = {k: ' '.join(p['text'] for p in v) for k, v in idx.items()}

print(f"{'교시':<6}" + ''.join(f'{k:>16}' for k in idx) + '   주제어')
print('─' * (6 + 16 * len(idx) + 40))

rows = []
for f in sorted(glob.glob(f'{day}/audio/p*.txt')):
    tx = open(f).read()
    mine = [t for t in TERMS if tx.count(t) >= 3]          # 이 교시의 주제어
    if not mine:
        print(f'{os.path.basename(f)[:3]:<6}' + '  (주제어 없음 — 오리엔테이션/Q&A 교시로 보임)')
        continue
    cells, best, best_k = '', 0.0, None
    for k, bk in books.items():
        hit = sum(1 for t in mine if bk.count(t) > 0)
        r = hit / len(mine)
        if r > best: best, best_k = r, k
        mark = '★' if r >= .7 else (' ' if r >= .3 else '·')
        cells += f'{hit:>7}/{len(mine):<4}{mark}{r:>3.0%}'
    print(f'{os.path.basename(f)[:3]:<6}{cells}   ' + ' '.join(mine[:6]))
    rows.append((os.path.basename(f)[:3], best_k, best))

print('\n=== 판정 ===')
for p, k, r in rows:
    if r >= .7:   print(f'  {p} → {k}  (확실, {r:.0%})')
    elif r >= .3: print(f'  {p} → {k}  (약함, {r:.0%}) — 참고로만 쓸 것')
    else:         print(f'  {p} → 대응 교본 없음 ({r:.0%}) — 녹취만으로 작성')

if rows and max(r for _, _, r in rows) < .3:
    print('\n⚠️  전 교시가 30% 미만이다. 교재가 이 강의의 것이 아닐 가능성이 높다.')
    print('    진행하지 말고 위 대조표를 근거로 사용자에게 확인할 것.')
