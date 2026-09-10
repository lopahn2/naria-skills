# 강의 노트 PDF 생성 (서브에이전트 없는 도구용)

서브에이전트/병렬 위임을 지원하지 않는 도구(단일 세션만 가능)에서 쓰는 순차 실행판이다.
원칙은 [`../../PRINCIPLES.md`](../../PRINCIPLES.md)와 동일 — 다른 건 Phase A/B2를
**위임하지 않고 한 세션이 순서대로 직접 수행**한다는 것뿐이다.

컨텍스트 절약 원칙은 서브에이전트가 없어도 그대로 지킨다:
**노트 파일(`notes/pMM.md`)을 다 쓴 교시는 그 원문(`audio/pMM.txt`)을 다시 열지 않는다.**
Phase B에서 통합본을 쓸 때 노트만 참조하고 원문으로 돌아가지 않으면, 8교시치 원문이
동시에 컨텍스트에 남아있는 것보다 훨씬 가볍다.

> **이 폴더(`vendors/generic/`)만 고칠 것.** `../claude/`, `../openai/`는 다른
> 벤더용이니 참고는 해도 내용을 바꾸지 않는다. 공통 방법론(`../../PRINCIPLES.md`,
> `../../scripts/`, `../../references/`)을 고칠 땐 다른 벤더의 실행 방식과
> 어긋나지 않는지 확인하고, 애매하면 사용자에게 먼저 묻는다.

## 실행 순서

### Phase 0 · 전처리

```bash
python3 ../../scripts/prep.py dayNN
python3 ../../scripts/idx_summary.py dayNN
python3 ../../scripts/match.py dayNN
```

`PRINCIPLES.md`의 등급(A/B/C)·매칭 임계값(70%/30%) 판정 기준을 그대로 적용한다.
전 교시 매칭이 다 낮으면 진행하지 말고 사용자에게 확인한다.

### Phase A · 교시 분석 (순차, 교시마다 하나씩)

각 교시에 대해:

1. `dayNN/audio/pMM.txt` 전문을 읽는다 (앞부분만 보고 추론하지 않는다).
2. 대응 교본 페이지가 있으면 그 구간을 확인하고, 이미지 위주 페이지는 직접 렌더해서 본다.
3. `../../references/chapter-note-spec.md` 스펙대로 `dayNN/notes/pMM.md`를 쓴다.
   **요약하지 말고 구조화한다** — 비유는 원문 인용 포함, 교차 후보를 반드시 채운다.
4. 아래로 `dayNN/cross.jsonl`에 한 줄 추가한다:
   ```bash
   echo '{"chapter":"p05","title":"<주제>","one_line":"<한 문장>","cross":["<개념>: <이유>"]}' \
     | python3 ../../scripts/append_cross.py dayNN
   ```
5. **이 교시의 노트를 다 쓰고 나면, 이 교시의 원문(`audio/pMM.txt`)은 이후 단계에서
   다시 열지 않는다.** 다음 교시로 넘어간다.

교시가 많으면(6개 이상) 한 세션의 컨텍스트가 부담스러울 수 있다 — 이 경우 며칠에
나눠 처리하거나, 노트를 다 쓴 직후 대화를 새로 시작해 이어가는 것도 방법이다
(단, `dayNN/notes/*.md`와 `cross.jsonl`은 파일로 남아있으므로 새 세션에서도 이어받을 수 있다).

### Phase B1 · 연결 지도와 목차 재설계

`dayNN/cross.jsonl`만 읽는다(노트 전체를 다시 열지 않는다). `PRINCIPLES.md`의 지침대로
"하루를 관통하는 한 문장"을 정하고, 주제 기반으로 `dayNN/outline.md`를 작성한다.

### Phase B2 · 파트 작성 (순차, 파트마다)

`outline.md`가 정한 장 구성대로 파트를 나눈다. 각 파트에 대해:

1. 그 파트가 담당하는 `notes/pMM.md`들만 읽는다 (**원문은 열지 않는다**).
2. `outline.md`에 적힌 장 제목·소제목을 그대로 따라 `partN.html`을 쓴다.
3. 도해는 `<img src="data:image/png;base64,{{key}}">` 형태로만 남긴다 — `{{key}}`를
   `<img>` 밖에 맨몸으로 쓰지 않는다.
4. 파트를 다 쓰면 **그 파트 본문을 다시 참조하지 않는다** — 조립은 스크립트가 파일에서 한다.

### Phase C · 렌더와 검증

```bash
python3 ../../scripts/build.py out/dayNN.pdf part1.html part2.html part3.html
python3 ../../scripts/verify.py out/dayNN.pdf
```

`verify.py`가 만든 컨택트 시트를 반드시 눈으로 확인한다(한글 깨짐, 도해 겹침, 빈 페이지 등).

### Phase D · OKF 변환 (선택)

```bash
python3 ../../scripts/build_okf.py <project> dayNN
```

`<project>` 이름은 묻지 않고 임의로 짓지 않는다.
