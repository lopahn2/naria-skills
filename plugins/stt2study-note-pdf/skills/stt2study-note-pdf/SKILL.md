---
name: stt2study-note-pdf
description: 강의 녹취록(STT)과 교재 PDF로 다이어그램 중심 학습 노트 PDF를 만든다. 교시별 분석을 서브에이전트에 위임하고 통합본은 메인이 작성한다. 인코딩·OCR·교본 매칭·STT 교정 자동 처리. 강의 정리, 교육 노트, 세미나·컨퍼런스 녹취 정리 요청에 사용.
use-agent-model: claude-sonnet-5(medium), gpt-5.6-terra(medium)
---

# 강의 노트 PDF 생성

**이 폴더 전체(`stt2study-note-pdf/`)가 이 스킬의 전부다.** 마켓플레이스 등록이나
플러그인 설치 없이, zip 다운로드나 `git clone`만으로 그대로 쓸 수 있게 만들었다 —
이 폴더를 통째로 복사해 각 도구가 스킬을 읽는 위치(예: Claude Code라면
`.claude/skills/stt2study-note-pdf/`)에 두면 된다. 위치·설치 방법은 문서 맨 끝
"이 폴더를 그대로 쓴다" 참조.

**서브에이전트를 부를 때 쓸 모델은 위 frontmatter의 `use-agent-model`에 명시돼
있다** — Claude Code면 `claude-sonnet-5`, Codex/ChatGPT Work면 `gpt-5.6-terra`,
둘 다 reasoning effort는 medium이다. 실행 환경이 이 중 어느 쪽도 아니거나 지정된
모델을 쓸 수 없으면, 임의로 다른 모델을 골라 조용히 진행하지 말고 반드시 사용자에게
먼저 확인받는다.

**먼저 `PRINCIPLES.md`를 읽어라.** 4대 원칙, 아키텍처, Phase 0~D의 판단
기준(등급, 매칭 임계값, 분량 기준, 사용자에게 확인할 것)이 전부 거기 있다.
이 파일은 그 원칙을 "서브에이전트를 실제로 어떻게 부르는가"로 옮기는
실행 지침만 다룬다.

## 실행 환경 판별

- **Claude Code / Cowork**라면 → 각 Phase의 "Claude Code" 분기를 따른다.
- **OpenAI Codex / ChatGPT Work**라면 → 각 Phase의 "Codex" 분기를 따른다.
- **서브에이전트 위임 자체를 지원하지 않는 도구**라면 → `generic-usage.md`를
  따른다(순차 실행판, 원칙은 동일).
- **셋 다 아니거나 판단이 애매하면** → 임의로 아무 분기나 적당히 따르지
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

이 스킬 폴더에는 이 역할에 맞춰 쓴 서브에이전트 페르소나가
`agents/lecture-chapter-analyst.md`에 있다 — 이 폴더가 Claude Code 플러그인으로
설치돼 있지 않은 한(즉 `stt2study-note-pdf:lecture-chapter-analyst`라는
subagent_type이 따로 등록돼 있지 않은 한), 이 파일을 직접 Read로 읽어
그 내용을 `general-purpose` 서브에이전트 프롬프트에 그대로 포함시켜 호출한다.

```
Agent(
  subagent_type: "general-purpose",   # 위 이름으로 별도 등록돼 있으면 그걸 우선 사용
  model: "claude-sonnet-5",
  description: "N교시 녹취 분석",
  prompt: "<agents/lecture-chapter-analyst.md 의 '절대 규칙'부터 '출력 스펙'까지 전문>

           <위 공통 지시>
           스펙 경로: references/chapter-note-spec.md"
)
```

어느 쪽이든 **모델은 `claude-sonnet-5`를 명시**한다(reasoning effort: medium).

### Codex일 때

`collaboration.spawn_agent`(또는 그에 준하는 서브에이전트 생성 기능)를 쓸 수
있는 환경에서는 교시마다 독립 에이전트로 위임하고, **model은 `gpt-5.6-terra`를
우선 사용한다** (reasoning effort: medium). 런타임이 특정 모델 선택을 지원하지
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

`agents/lecture-part-writer.md`를 Read로 읽어 그 내용을 프롬프트에 포함시킨다
(Phase A와 같은 이유 — 별도 subagent_type으로 등록돼 있지 않을 수 있다).

```
Agent(
  subagent_type: "general-purpose",
  model: "claude-sonnet-5",
  description: "N파트(2장~4장) 작성",
  prompt: "<agents/lecture-part-writer.md 전문>

           <위 공통 지시>
           dayNN/notes/p04.md, dayNN/notes/p05.md 를 읽고,
           <outline.md에서 이 파트가 담당할 장들의 항목만 그대로 붙여넣기>
           연결 지도: <B1에서 이 파트와 관련된 항목만 추려서 전달>"
)
```

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

## 이 폴더를 그대로 쓴다

이 스킬은 마켓플레이스·플러그인 형식에 얽매이지 않는다. `stt2study-note-pdf/`
폴더 하나가 원본이자 배포 단위다:

```
stt2study-note-pdf/
├── SKILL.md              (이 파일)
├── PRINCIPLES.md          방법론 — 먼저 읽을 것
├── generic-usage.md       서브에이전트 없는 도구용 순차 실행판
├── agents/                Claude Code 서브에이전트 페르소나(참고용 프롬프트)
├── references/            스펙·규칙 문서
├── scripts/                실행 스크립트
└── assets/                 렌더 템플릿(CSS 등)
```

- **zip으로 받았다면**: 압축을 풀어 이 폴더 전체를 그대로 쓴다.
- **git clone으로 받았다면**: 저장소 안에서 `skills/stt2study-note-pdf/`가 이 폴더다.
- **Claude Code**: 이 폴더를 `.claude/skills/stt2study-note-pdf/`(프로젝트) 또는
  사용자 스킬 디렉터리에 복사한다. `agents/*.md`를 Claude Code의 서브에이전트
  등록 규칙에 맞는 위치에도 함께 두면 `subagent_type`으로 바로 호출할 수 있지만,
  두지 않아도 위 "Claude Code일 때" 분기처럼 파일 내용을 프롬프트에 포함시켜
  `general-purpose`로 대체 호출하면 된다 — 필수는 아니다.
- **Codex / ChatGPT Work, 그 외 서브에이전트 개념이 없는 도구**: 이 폴더를
  통째로 프로젝트에 두고 `SKILL.md`(또는 서브에이전트가 없다면
  `generic-usage.md`)부터 읽게 하면 된다.

벤더별로 별도 사본을 만들거나 빌드 스크립트로 동기화할 필요가 없다 — 파일이
하나뿐이므로 어긋날 것도 없다.
