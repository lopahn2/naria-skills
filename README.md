# naria-skills

naria가 만든 AI 에이전트 스킬 모음. 벤더 중립을 목표로 한다 — 각 스킬은
공통 방법론을 벤더 무관 문서로 두고, 도구별 실행 방식(서브에이전트 호출 문법,
플러그인 형식 등)만 `vendors/`로 나눈다.

## 스킬 목록

| 스킬 | 설명 |
|---|---|
| [`stt2study-note-pdf`](skills/stt2study-note-pdf/) | 강의 녹취록(STT)과 교재 PDF로 다이어그램 중심 학습 노트 PDF 생성 |

## 구조

```
naria-skills/
├── README.md                     이 파일
├── LICENSE
├── .claude-plugin/
│   └── marketplace.json          Claude Code/Cowork용 마켓플레이스 매니페스트
├── .agents/plugins/
│   └── marketplace.json          ChatGPT Work/Codex용 마켓플레이스 매니페스트
├── plugins/
│   └── stt2study-note-pdf -> skills/stt2study-note-pdf/vendors/openai
│                                  Codex 마켓플레이스가 참조하는 OpenAI 플러그인 진입점
└── skills/
    └── <스킬 이름>/
        ├── README.md              그 스킬의 개요 + 벤더별 안내
        ├── PRINCIPLES.md          벤더 중립 원칙 (모든 스킬이 이 패턴을 따르진 않아도 됨 —
        │                          여러 벤더를 지원하는 스킬만 이렇게 나눈다)
        ├── scripts/, references/, assets/   벤더 무관 자산 (해당하면)
        └── vendors/
            ├── claude/            Claude Code 플러그인 형식
            ├── openai/            GPT 계열용 (해당하면)
            └── generic/           서브에이전트 미지원 도구용 (해당하면)
```

모든 스킬이 `vendors/` 구조를 가질 필요는 없다 — 멀티벤더 지원이 실제로 의미 있는
스킬만 이렇게 나누고, 단순한 스킬은 스킬 폴더 안에 `SKILL.md` 하나로 끝내도 된다.

## 벤더 간 규칙

**각 모델/도구는 자기 `vendors/<자신>/` 폴더만 고친다. 다른 벤더의 `vendors/<다른 벤더>/`는
읽어서 참고할 순 있어도 내용을 고치지 않는다.** 예를 들어 GPT 계열 모델이
`vendors/openai/`의 TODO를 채울 때 `vendors/claude/`나 `vendors/generic/`은 건드리지
않는다. 공통 방법론(`PRINCIPLES.md`, `scripts/`, `references/`, `assets/`)을 고쳐야 하면
그건 벤더 전용이 아니므로 고쳐도 되지만, 그 변경이 다른 벤더의 실행 방식과 어긋나지
않는지는 신경 써야 한다 — 애매하면 사용자에게 먼저 확인한다.

## Claude Code / Cowork에서 쓰기

이 리포를 마켓플레이스로 추가하면 `.claude-plugin/marketplace.json`에 등록된
플러그인을 설치할 수 있다.

```
/plugin marketplace add naria/naria-skills
/plugin install stt2study-note-pdf
```

(정확한 명령/문법은 사용 중인 Claude Code 버전의 플러그인 문서를 확인할 것 —
마켓플레이스 매니페스트 스펙은 계속 바뀔 수 있으므로, 처음 푸시한 뒤
로컬에서 `/plugin marketplace add ./` 로 한 번 검증해볼 것을 권한다.)

## 다른 도구에서 쓰기

스킬마다 `vendors/` 아래에 해당 도구용 폴더가 있으면 그걸 읽는다. 없으면
(아직 TODO거나 애초에 그 스킬이 멀티벤더를 지원하지 않으면) 그 스킬의
`README.md`를 참고해 직접 방법을 채운다.

## ChatGPT Work / Codex에서 쓰기

ChatGPT Work/Codex는 `.agents/plugins/marketplace.json`을 마켓플레이스 매니페스트로 읽는다.
`plugins/stt2study-note-pdf`는 `skills/stt2study-note-pdf/vendors/openai`를 가리키는 심볼릭 링크이며,
실제 플러그인 매니페스트는 그 안의 `.codex-plugin/plugin.json`에 있다.

로컬에서 이 레포를 마켓플레이스로 추가할 때는 레포 루트를 대상으로 한다.

```bash
codex plugin marketplace add .
```

GitHub에서 설치할 때의 정확한 URL 문법은 사용하는 Codex 클라이언트의 Marketplace 추가 화면이나
현재 버전의 안내를 따른다. 설치 뒤에는 `stt2study-note-pdf` 플러그인을 선택하면 된다.

## 라이선스

[MIT](LICENSE) — 각 스킬 폴더에 별도 명시가 없는 한 리포 전체에 적용.
