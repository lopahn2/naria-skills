---
name: lecture-note-pdf
description: 강의 녹취록(STT)과 교재 PDF로 다이어그램 중심 학습 노트 PDF를 만든다. 교시별 분석을 서브에이전트에 위임하고 통합본은 메인이 작성한다. 인코딩·OCR·교본 매칭·STT 교정 자동 처리. 강의 정리, 교육 노트, 세미나·컨퍼런스 녹취 정리 요청에 사용.
---

# 강의 노트 PDF 생성 (Claude Code / Cowork 전용)

**먼저 `PRINCIPLES.md`를 읽어라.** 4대 원칙, 아키텍처, Phase 0~D의 판단 기준(등급,
매칭 임계값, 분량 기준, 사용자에게 확인할 것)이 전부 거기 있다. 이 파일은 그 원칙을
Claude Code의 Task(서브에이전트) 도구로 실행하는 방법만 다룬다.

> **이 스킬을 고칠 때는 이 폴더(`vendors/claude/`)만 고친다.** `../openai/`,
> `../generic/`은 다른 벤더용이니 읽어서 참고는 해도 내용을 바꾸지 않는다.
> 공통 방법론(`PRINCIPLES.md`, `../../scripts/`, `../../references/`)을 고칠 땐 다른
> 벤더의 실행 방식과 어긋나지 않는지 확인하고, 애매하면 사용자에게 먼저 묻는다.

## Phase A · 교시 분석 (서브에이전트)

교시마다 하나씩, **병렬로** 띄운다.

```
Agent(
  subagent_type: "lecture-chapter-analyst",
  model: "sonnet",
  description: "N교시 녹취 분석",
  prompt: "dayNN/audio/pMM.txt 를 정독해 dayNN/notes/pMM.md 를 만들어라.
           대응 교본: <파일> p.A–B (신뢰도 <높음/낮음/없음>)
           스펙: ${CLAUDE_PLUGIN_ROOT}/skills/lecture-note-pdf/references/chapter-note-spec.md
           요약하지 말고 구조화하라. 비유는 원문 인용을 포함하라.
           교차 후보를 반드시 채워라. 다 쓴 뒤 dayNN/cross.jsonl 에
           append_cross.py 로 한 줄 추가하라. 반환은 5줄 이내."
)
```

`lecture-chapter-analyst` 에이전트가 없으면 `general-purpose`에 스펙 경로를 주고
같은 지시를 내린다. 어느 쪽이든 **`model: "sonnet"`을 명시**한다.

교시들이 같은 `dayNN/cross.jsonl`에 병렬로 append해도 깨지지 않는다 —
`append_cross.py`가 한 줄을 한 번의 write()로 쓰기 때문이다. 잠금도 병합 단계도 필요 없다.

```bash
echo '{"chapter":"p05","title":"<주제>","one_line":"<한 문장>","cross":["<개념>: <이유>"]}' \
  | python3 ${CLAUDE_PLUGIN_ROOT}/skills/lecture-note-pdf/scripts/append_cross.py dayNN
```

## Phase B2 · 파트 작성 (서브에이전트, 병렬)

```
Agent(
  subagent_type: "lecture-part-writer",
  model: "sonnet",
  description: "N파트(2장~4장) 작성",
  prompt: "dayNN/notes/p04.md, dayNN/notes/p05.md 를 읽고,
           dayNN/outline.md 에서 아래 장만 맡아 partN.html 을 써라.
           <outline.md에서 이 파트가 담당할 장들의 항목만 그대로 붙여넣기>
           장 제목·소제목(N.1, N.2...)은 outline.md에 적힌 대로 따르고
           임의로 바꾸지 마라. 연결 지도: <B1에서 이 파트와 관련된 항목만 추려서 전달>
           도해는 노트의 ✅ 표시만 <img src=\"data:image/png;base64,{{key}}\"> 형태로
           남겨라 — {{key}}를 <img> 밖에 맨몸으로 쓰면 나중에 이미지 대신
           base64 텍스트가 그대로 인쇄된다. 원문 녹취는 열지 마라. 반환은 5줄 이내."
)
```

`lecture-part-writer` 에이전트가 없으면 `general-purpose`에 스펙 경로를 주고
같은 지시를 내린다. 어느 쪽이든 **`model: "sonnet"`을 명시**한다. 파트가 담당 밖
교시와의 연결을 지어내지 않도록, 연결 지도는 그 파트에 해당하는 항목만 잘라서 준다.

## 여러 날을 한꺼번에

날짜 단위로 Phase A~C 전체를 서브에이전트에 위임한다. 날짜 간 교차 연결은 교시 간보다
약하므로 잃는 것이 적다. 마지막에 메인이 누적 용어집만 병합한다.

**날짜를 넘나드는 흐름을 찾을 때는 지난 날짜의 `notes/*.md`를 다시 열지 말고
`day*/cross.jsonl`만 읽는다.**

```bash
cat day0*/cross.jsonl
```

## 증분 처리

`dayNN/manifest.json`에 처리 완료된 교시와 입력 파일 해시를 기록한다. 5일차를 돌릴 때
1~4일차 원문을 다시 읽지 않는 것이 토큰 절감의 최대 지점이다. 용어집은 누적하되 이미
등록된 항목은 다시 쓰지 않는다.

## 구성

이 폴더(`vendors/claude/`)에는 Claude Code 플러그인 형식(`.claude-plugin/plugin.json`,
`agents/*.md`, 이 `SKILL.md`)만 있다. `scripts/`, `references/`, `assets/`,
`PRINCIPLES.md`는 이 벤더 전용 사본이 아니라 스킬 루트(`skills/lecture-note-pdf/`)를
가리키는 심볼릭 링크다 — 여러 벤더가 같은 스크립트·참고문서·원칙 문서를 공유하기
위함이니, 내용을 고칠 때는 링크가 아니라 스킬 루트의 원본을 수정할 것.
