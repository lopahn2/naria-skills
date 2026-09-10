---
name: stt2study-note-pdf
description: 강의 녹취록(STT)과 교재 PDF로 다이어그램 중심 학습 노트 PDF를 만든다. 교시별 분석을 서브에이전트에 위임하고 통합본은 메인이 작성한다. 인코딩·OCR·교본 매칭·STT 교정 자동 처리. 강의 정리, 교육 노트, 세미나·컨퍼런스 녹취 정리 요청에 사용.
---

# 강의 노트 PDF 생성

**이 파일이 이 스킬의 유일한 원본이다.** Claude Code용과 Codex용 SKILL.md가
따로 존재하지 않는다 — 아래 각 실행 단계는 환경에 따라 분기하라고 명시돼
있으니, 지금 자신이 어떤 도구로 실행되고 있는지 먼저 판단하고 해당 분기를
따른다. (벤더별 패키징 위치는 문서 맨 끝 "벤더별 패키징" 참조.)

**먼저 `PRINCIPLES.md`를 읽어라.** 4대 원칙, 아키텍처, Phase 0~D의 판단
기준(등급, 매칭 임계값, 분량 기준, 사용자에게 확인할 것)이 전부 거기 있다.
이 파일은 그 원칙을 "서브에이전트를 실제로 어떻게 부르는가"로 옮기는
실행 지침만 다룬다.

## 실행 환경 판별

- **Claude Code / Cowork**라면 → 각 Phase의 "Claude Code" 분기를 따른다.
- **OpenAI Codex / ChatGPT Work**라면 → 각 Phase의 "Codex" 분기를 따른다.
- **둘 다 아니거나 판단이 애매하면** → 임의로 아무 분기나 적당히 따르지
  말고, 서브에이전트를 어떻게 호출해야 하는지(가능 여부, 모델 선택 가능
  여부) 사용자에게 먼저 확인받은 뒤 진행한다. 애매한 채로 진행해서 나중에
  "그럴듯하지만 틀린" 설명을 지어내는 것이 가장 나쁜 실패다.

## Phase A · 교시 분석 (서브에이전트, 병렬)

공통 지시 (환경 무관 — 아래 두 분기 모두 이 내용을 그대로 전달한다):

> `dayNN/audio/pMM.txt`를 정독해 `dayNN/notes/pMM.md`를 만들어라.
> 대응 교본: `<파일>` p.A–B (신뢰도 `<높음/낮음/없음>`)
> 스펙: `references/chapter-note-spec.md`
> 요약하지 말고 구조화하라. 비유는 원문 인용을 포함하라.
> 교차 후보를 반드시 채워라. 다 쓴 뒤 `dayNN/cross.jsonl`에
> `append_cross.py`로 한 줄 추가하라. 반환은 5줄 이내.

### Claude Code일 때

```
Agent(
  subagent_type: "lecture-chapter-analyst",
  model: "sonnet",
  description: "N교시 녹취 분석",
  prompt: "<위 공통 지시>
           스펙 경로: ${CLAUDE_PLUGIN_ROOT}/skills/stt2study-note-pdf/references/chapter-note-spec.md"
)
```

`lecture-chapter-analyst` 에이전트가 없으면 `general-purpose`에 스펙 경로를
주고 같은 지시를 내린다. 어느 쪽이든 **`model: "sonnet"`을 명시**한다.

### Codex일 때

`collaboration.spawn_agent`(또는 그에 준하는 서브에이전트 생성 기능)를 쓸 수
있는 환경에서는 교시마다 독립 에이전트로 위임하고, **model은
`gpt-5.6-terra`를 우선 사용한다.** 런타임이 특정 모델 선택을 지원하지
않으면, 임의로 다른 모델을 쓰지 말고 반드시 사용자에게 확인 후 서브에이전트를
생성한다. 위 공통 지시를 그대로 전달한다.

### 공통

교시들이 같은 `dayNN/cross.jsonl`에 병렬로 append해도 깨지지 않는다 —
`append_cross.py`가 한 줄을 한 번의 write()로 쓰기 때문이다. 잠금도 병합
단계도 필요 없다.

```bash
echo '{"chapter":"p05","title":"<주제>","one_line":"<한 문장>","cross":["<개념>: <이유>"]}' \
  | python3 scripts/append_cross.py dayNN
```

교시가 3개 이하면 위임하지 않고 메인이 직접 처리해도 된다 — 오버헤드가
이득보다 크다.

## Phase B2 · 파트 작성 (서브에이전트, 병렬)

공통 지시 (환경 무관):

> 담당 `dayNN/notes/pMM.md`들을 읽고, `dayNN/outline.md`에서 맡은 장만
> `partN.html`로 써라. 장 제목·소제목(N.1, N.2...)은 `outline.md`에 적힌
> 대로 따르고 임의로 바꾸지 마라. 연결 지도는 이 파트와 관련된 항목만
> 전달받은 것이다.
>
> **도해는 노트의 `✅`(원본 사용) 표시만** `<img src="data:image/png;base64,{{key}}">`
> 형태로 남겨라 — `{{key}}`를 `<img>` 밖에 맨몸으로 쓰면 base64 텍스트가
> 그대로 인쇄된다. **원본 사용으로 판정된 도해를 직접 그린 그림으로 임의
> 대체하지 마라** — `references/diagram-rules.md` 위반이며, 추출이
> 번거롭다는 이유로 이 규칙을 건너뛰는 것 자체가 실패다. 정말 원본을 쓸 수
> 없는 기술적 사유(추출 실패·손상 등)가 있으면 조용히 대체하지 말고
> 사용자에게 먼저 알린다.
>
> **노트의 `## 현장 사례`에 실제 내용이 있는 항목은 전부 `.example` 박스로
> 옮겨라** — 한두 문장으로 일반화해 압축하지 마라. 구체적 사례(등장·수치·
> 전개)가 살아 있어야 한다. 형식은 `references/document-structure.md`의
> "강사의 실제 예시 박스" 참조.
>
> 원문 녹취는 열지 마라. 반환은 5줄 이내.

### Claude Code일 때

```
Agent(
  subagent_type: "lecture-part-writer",
  model: "sonnet",
  description: "N파트(2장~4장) 작성",
  prompt: "<위 공통 지시>
           dayNN/notes/p04.md, dayNN/notes/p05.md 를 읽고,
           <outline.md에서 이 파트가 담당할 장들의 항목만 그대로 붙여넣기>
           연결 지도: <B1에서 이 파트와 관련된 항목만 추려서 전달>"
)
```

`lecture-part-writer` 에이전트가 없으면 `general-purpose`에 스펙 경로를
주고 같은 지시를 내린다. 어느 쪽이든 **`model: "sonnet"`을 명시**한다.

### Codex일 때

Phase A와 동일하게 `gpt-5.6-terra`를 우선 사용하고, 지원하지 않으면
사용자에게 확인 후 진행한다. 위 공통 지시를 그대로 전달한다.

### 공통

파트가 담당 밖 교시와의 연결을 지어내지 않도록, 연결 지도는 그 파트에
해당하는 항목만 잘라서 준다. 교시가 3개 이하거나 파트가 1~2개뿐이면
위임하지 않고 메인이 직접 써도 된다 — 이때도 `outline.md` 작성은
생략하지 않는다.

## 여러 날을 한꺼번에

날짜 단위로 Phase A~C 전체를 서브에이전트에 위임한다. 날짜 간 교차 연결은
교시 간보다 약하므로 잃는 것이 적다. 마지막에 메인이 누적 용어집만 병합한다.

**날짜를 넘나드는 흐름을 찾을 때는 지난 날짜의 `notes/*.md`를 다시 열지
말고 `day*/cross.jsonl`만 읽는다.**

```bash
cat day0*/cross.jsonl
```

## 증분 처리

`dayNN/manifest.json`에 처리 완료된 교시와 입력 파일 해시를 기록한다.
5일차를 돌릴 때 1~4일차 원문을 다시 읽지 않는 것이 토큰 절감의 최대
지점이다. 용어집은 누적하되 이미 등록된 항목은 다시 쓰지 않는다.

## 벤더별 패키징

이 파일(`skills/stt2study-note-pdf/SKILL.md`)과 `PRINCIPLES.md`·`scripts/`·
`references/`·`assets/`가 이 스킬의 유일한 원본이다. 마켓플레이스 패키징은
이 원본을 그대로 노출할 뿐 별도 사본을 두지 않는다:

- **Claude Code** (`.claude-plugin/marketplace.json`) →
  `marketplace/claude/stt2study-note-pdf/` — 이 폴더 안의 `skills/stt2study-note-pdf/`는
  이 원본을 가리키는 심볼릭 링크. `agents/*.md`(서브에이전트 정의)만
  Claude Code 고유 메커니즘이라 여기 실체로 존재한다.
- **Codex** (`.agents/plugins/marketplace.json`) →
  `marketplace/codex/stt2study-note-pdf/` — Codex가 심볼릭 링크를 못 읽어서
  빌드 시 이 원본을 그대로 복사해 넣는다(`tools/build_codex_package.py`,
  CI가 자동 실행). **이 안의 파일은 손으로 고치지 않는다** — 다음 빌드에서
  덮어써진다. 내용을 고칠 땐 항상 이 파일(원본)만 고친다.
