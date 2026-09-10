# naria-skills

naria가 만든 AI 에이전트 스킬 모음. 각 스킬은 `SKILL.md` 원본이 **하나뿐**이다 —
Claude Code용/Codex용으로 내용이 갈라진 별도 파일을 두지 않는다. 벤더마다 다르게
호출해야 하는 부분(서브에이전트 모델 지정 등)은 그 `SKILL.md` 안에서 "지금 어떤
환경인지 판별해 분기를 따르라"고 지시하고, 판단이 애매하면 사용자에게 먼저
확인받도록 명시한다. 마켓플레이스에 올라가는 패키징(Claude/Codex)은 이 원본을
감싸는 얇은 껍데기일 뿐, 별도의 콘텐츠 사본이 아니다.

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
├── tools/
│   ├── sync_plugin_version.py    벤더별 plugin.json 버전을 하나로 맞춤
│   └── build_codex_package.py    Codex 패키징을 스킬 원본과 다시 맞춤 (심볼릭 링크 대체)
├── skills/
│   └── <스킬 이름>/               스킬의 유일한 원본 — 이 안의 내용만 고친다
│       ├── README.md
│       ├── SKILL.md               실행 지침 (벤더 분기 포함)
│       ├── PRINCIPLES.md          방법론 (벤더 무관)
│       ├── scripts/, references/, assets/
│       └── generic-usage.md       서브에이전트 없는 도구용 (마켓플레이스 패키징 아님, 해당하면)
└── marketplace/                  마켓플레이스가 실제로 읽는 패키징 — 전부 빌드 산출물이거나
    │                              심볼릭 링크. 여기는 직접 편집하지 않는다.
    ├── claude/<스킬 이름>/
    │   ├── .claude-plugin/plugin.json
    │   ├── agents/*.md            Claude Code 고유 서브에이전트 정의 (여긴 실체)
    │   └── skills/<스킬 이름>/     스킬 원본을 가리키는 심볼릭 링크
    └── codex/<스킬 이름>/
        ├── .codex-plugin/plugin.json
        └── skills/<스킬 이름>/     스킬 원본의 복사본 (심볼릭 링크 불가라 빌드 산출물)
```

모든 스킬이 `marketplace/` 패키징을 가질 필요는 없다 — 마켓플레이스에 올릴 필요가
없는 단순한 스킬은 `skills/<이름>/SKILL.md` 하나로 끝내도 된다.

## 원본과 패키징을 분리하는 이유

**`skills/<이름>/`만 사람이 고치는 원본이다.** `marketplace/` 아래는 전부 그 원본을
노출하는 방식일 뿐이다 — Claude는 심볼릭 링크로(고치면 자동 반영), Codex는
심볼릭 링크를 못 읽어서 빌드 시 파일로 복사한다(`tools/build_codex_package.py`,
CI가 자동 실행). 예전에는 벤더마다 `SKILL.md`를 손으로 따로 관리했는데, 그 결과
같은 규칙이 벤더마다 다르게 적히거나 한쪽만 갱신되는 문제가 반복됐다 — 지금은
원본이 하나뿐이라 그 문제 자체가 없어졌다.

새 벤더를 추가할 때도 `skills/<이름>/SKILL.md` 안에 그 벤더의 분기를 추가하고,
`marketplace/<벤더>/<이름>/`에 그 벤더 형식의 `plugin.json`만 새로 만들면 된다 —
스킬 내용을 다시 쓰지 않는다.

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

## ChatGPT Work / Codex에서 쓰기

ChatGPT Work/Codex는 `.agents/plugins/marketplace.json`을 마켓플레이스 매니페스트로
읽는다. `marketplace/codex/stt2study-note-pdf/`가 Codex가 실제로 설치하는 패키징이며,
`skills/stt2study-note-pdf/`(원본)를 그대로 복사한 것이다(Codex가 심볼릭 링크를 못
읽어서 심볼릭 링크 없이 파일로 둔다). 실제 플러그인 매니페스트는 그 안의
`.codex-plugin/plugin.json`에 있다.

로컬에서 이 레포를 마켓플레이스로 추가할 때는 레포 루트를 대상으로 한다.

```bash
codex plugin marketplace add .
```

GitHub에서 설치할 때의 정확한 URL 문법은 사용하는 Codex 클라이언트의 Marketplace
추가 화면이나 현재 버전의 안내를 따른다. 설치 뒤에는 `stt2study-note-pdf` 플러그인을
선택하면 된다.

## 다른 도구에서 쓰기

`marketplace/`에 해당 벤더 패키징이 없으면(마켓플레이스에 올릴 필요가 없는
도구라면), 그 스킬의 `generic-usage.md`(있으면) 또는 `README.md`를 참고해 직접
방법을 채운다. `SKILL.md`·`PRINCIPLES.md`·`scripts/`·`references/`·`assets/`는
어떤 도구를 쓰든 그대로 쓸 수 있다 — 벤더 전용이 아니다.

## 패키징 동기화

원본(`skills/**`)을 고치면 Codex 패키징(`marketplace/codex/`)과 각 `plugin.json`
버전이 자동으로 따라오게 만들어져 있다.

```bash
python3 tools/build_codex_package.py          # skills/ -> marketplace/codex/ 복사 동기화
python3 tools/sync_plugin_version.py          # 벤더별 plugin.json 버전 통일
python3 tools/build_codex_package.py --check  # 실행 없이 어긋남만 확인 (exit 1)
python3 tools/sync_plugin_version.py --check  # 위와 동일, 버전용
```

`.github/workflows/sync-plugin-version.yml`이 `skills/**` 또는 `plugin.json`이 바뀐
채로 main에 push될 때마다 이 두 스크립트를 자동으로 돌리고, 바뀐 게 있으면 다시
커밋한다 — 사람이 원본만 고쳐서 push하면 `marketplace/codex/`와 버전은 CI가 맞춘다.
`marketplace/claude/`는 심볼릭 링크라 애초에 어긋날 일이 없다.

## 라이선스

[MIT](LICENSE) — 각 스킬 폴더에 별도 명시가 없는 한 리포 전체에 적용.
