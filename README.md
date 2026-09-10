# naria-skills

naria가 만든 AI 에이전트 스킬 모음. 마켓플레이스·플러그인 형식에 얽매이지
않는다 — 각 스킬은 `skills/<이름>/` 폴더 하나가 전부이며, zip으로 받든
`git clone`으로 받든 그 폴더를 그대로 복사해 쓰면 된다. 설치 절차, 벤더별
사본, 빌드 동기화가 필요 없다.

벤더마다 다르게 호출해야 하는 부분(서브에이전트 모델 지정 등)은 각 스킬의
`SKILL.md` 안에서 "지금 어떤 환경인지 판별해 분기를 따르라"고 지시하고, 쓸
모델은 `SKILL.md` frontmatter의 `use-agent-model`에 실제 모델명으로 못박아
둔다. 판단이 애매하면 사용자에게 먼저 확인받도록 명시한다.

## 스킬 목록

| 스킬 | 설명 |
|---|---|
| [`stt2study-note-pdf`](skills/stt2study-note-pdf/) | 강의 녹취록(STT)과 교재 PDF로 다이어그램 중심 학습 노트 PDF 생성 |

## 구조

```
naria-skills/
├── README.md                     이 파일
├── LICENSE
└── skills/
    └── <스킬 이름>/               스킬의 전부 — 이 폴더 하나가 배포 단위
        ├── README.md
        ├── SKILL.md               실행 지침 — 벤더 분기 + use-agent-model
        ├── PRINCIPLES.md          방법론 (벤더 무관)
        ├── generic-usage.md       서브에이전트 없는 도구용 (해당하면)
        ├── agents/                Claude Code 서브에이전트 페르소나 (해당하면)
        ├── scripts/
        ├── references/
        └── assets/
```

## 왜 이렇게 단순한가

이전에는 Claude Code/Codex 마켓플레이스에 자동으로 뜨도록 `.claude-plugin/`,
`.agents/plugins/`, 벤더별 `marketplace/` 패키징(심볼릭 링크·빌드 스크립트·
CI 자동 동기화)까지 만들었다. 그런데 이걸 유지하는 비용이 이득보다 커졌다 —
벤더마다 마켓플레이스 매니페스트 스펙이 다르고 자주 바뀌며, Codex는 심볼릭
링크를 못 읽는 버그가 있어 빌드 복사본을 CI로 계속 맞춰야 했고, 그 와중에
정작 스킬 내용(이 레포의 진짜 값어치)과 무관한 배관 문제가 계속 생겼다.

그래서 원점으로 돌아왔다: **폴더 하나, 파일로 직접 쓰는 배포.** 마켓플레이스
등록이 주는 편의(검색·자동 업데이트)는 포기하지만, zip 다운로드나 `git clone`
만으로 어떤 도구에서든 즉시 쓸 수 있고 어긋날 사본도 없다.

## 스킬을 쓰는 법 (모든 스킬 공통)

1. 이 저장소를 zip으로 받거나 `git clone`한다.
2. 쓰려는 스킬의 `skills/<이름>/` 폴더 전체를 복사한다.
3. 사용 중인 도구가 스킬을 읽는 위치에 그 폴더를 둔다.
   - **Claude Code / Cowork**: `.claude/skills/<이름>/`(프로젝트) 또는 사용자
     스킬 디렉터리. 스킬에 `agents/*.md`가 있으면 Claude Code 서브에이전트
     정의 형식(frontmatter에 `model`, `reasoning_effort`)으로 쓰여 있어 그대로
     등록해도 되고, 등록하지 않아도 `SKILL.md`가 대체 호출 방법을 안내한다.
   - **OpenAI Codex / ChatGPT Work**: 폴더를 프로젝트에 두고 `SKILL.md`부터
     읽게 한다.
   - **서브에이전트 개념이 없는 도구**: 스킬에 `generic-usage.md`가 있으면
     그걸 따른다(순차 실행판).
4. 스킬의 `SKILL.md`가 "먼저 읽어라"라고 가리키는 문서(대개 `PRINCIPLES.md`)를
   먼저 읽고 시작한다.

각 스킬의 세부 사항(요구 사항, 디렉터리 구조, 실패 사례)은 그 스킬의
`README.md`를 참조한다.

## 라이선스

[MIT](LICENSE) — 각 스킬 폴더에 별도 명시가 없는 한 리포 전체에 적용.
