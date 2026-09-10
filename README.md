# naria-skills

naria가 만든 AI 에이전트 스킬 모음이다. 사람이 수정하는 유일한 원본은 `main`의
`plugins/<plugin-name>/`이다. 이 구조는 Claude Marketplace 플러그인 구조이면서
일반 도구에서 사용할 스킬 파일의 원본이기도 하다.

## 배포 방식

| 사용 환경 | 사용할 브랜치/경로 |
| --- | --- |
| 일반 도구 / ZIP | `main/plugins/<plugin-name>/skills/<skill-name>/` |
| Claude Code / Cowork | `main` Marketplace |
| ChatGPT Work / Codex | `openai-marketplace` 브랜치 |

`openai-marketplace`는 자동 생성되는 OpenAI 전용 배포 브랜치다. 직접 수정하지 않는다.

## 스킬 목록

| 스킬 | 설명 |
| --- | --- |
| [`stt2study-note-pdf`](plugins/stt2study-note-pdf/) | 강의 녹취록(STT)과 교재 PDF로 다이어그램 중심 학습 노트 PDF 생성 |

## 설치

아래의 `<plugin-name>`, `<skill-name>`은 설치하려는 항목의 실제 이름으로 바꾼다.
현재 두 이름은 동일하게 관리한다. 설치 가능한 이름은 위 스킬 목록 또는 Marketplace
목록에서 확인한다.

### ZIP / 일반 도구

원하는 플러그인만 sparse checkout으로 받은 뒤, 그 안의 스킬 폴더 전체를 ZIP으로
압축하거나 사용하는 도구의 skill 디렉터리에 복사한다.

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/lopahn2/naria-skills.git
cd naria-skills
git sparse-checkout set plugins/<plugin-name>
```

실제로 사용할 폴더는 다음이다.

```text
plugins/<plugin-name>/skills/<skill-name>/
```

### Claude Code / Cowork

Claude는 `main`을 Marketplace로 사용한다. Marketplace를 한 번 등록한 뒤,
필요한 플러그인만 설치한다.

```bash
claude plugin marketplace add lopahn2/naria-skills --sparse .claude-plugin plugins
claude plugin install <plugin-name>@naria-skills
```

현재 Marketplace와 설치 가능한 플러그인 확인:

```bash
claude plugin marketplace list
claude plugin list
```

업데이트:

```bash
claude plugin marketplace update naria-skills
claude plugin update <plugin-name>@naria-skills
```

Claude Desktop/Cowork Marketplace UI에서도 `lopahn2/naria-skills`를 등록한 뒤,
원하는 플러그인을 선택해 설치한다. 별도 branch ref는 지정하지 않는다.

### ChatGPT Work / Codex

OpenAI Marketplace에는 `openai-marketplace` 브랜치를 등록한다. Marketplace 등록은
한 번만 수행하고, 이후 원하는 플러그인을 설치한다.

```bash
codex plugin marketplace add lopahn2/naria-skills --ref openai-marketplace
codex plugin add <plugin-name>@naria-skills
```

설치 가능한 항목 확인:

```bash
codex plugin marketplace list
codex plugin list
```

설치 또는 업데이트 뒤에는 새 대화를 시작해야 새 스킬 목록이 반영될 수 있다.

## 새 스킬 추가

```text
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        └── ... 나머지 파일
```

- 현재 `plugin-name`, `skill-name`, `SKILL.md` frontmatter의 `name`,
  `.claude-plugin/plugin.json`의 `name`은 동일하게 관리한다.
- 새 Claude 플러그인은 루트 `.claude-plugin/marketplace.json`의 `plugins` 배열에도 추가한다.
- main에 push하면 `plugins/*/.claude-plugin/plugin.json`과
  `plugins/*/skills/*/SKILL.md`를 검증해 `openai-marketplace`를 갱신한다.

## 원본 수정 규칙

- `main/plugins/**`만 수정한다.
- `openai-marketplace`에는 직접 커밋하지 않는다.
- 배포본은 symlink를 쓰지 않는다.

## 라이선스

[MIT](LICENSE)
