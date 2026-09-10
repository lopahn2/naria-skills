# naria-skills

naria가 만든 AI 에이전트 스킬 모음이다. 사람이 수정하는 유일한 원본은 `main`의
`plugins/<플러그인 이름>/`이다. 이 구조는 Claude Marketplace 플러그인 구조이면서
일반 도구에서 사용할 스킬 파일의 원본이기도 하다.

## 배포 방식

| 사용 환경 | 사용할 브랜치/경로 |
| --- | --- |
| 일반 도구 / ZIP | `main/plugins/<플러그인>/skills/<스킬>/` |
| Claude Code / Cowork | `main` Marketplace |
| ChatGPT Work / Codex | `openai-marketplace` 브랜치 |

`openai-marketplace`는 자동 생성되는 OpenAI 전용 배포 브랜치다. 직접 수정하지 않는다.

## 스킬 목록

| 스킬 | 설명 |
| --- | --- |
| [`stt2study-note-pdf`](plugins/stt2study-note-pdf/) | 강의 녹취록(STT)과 교재 PDF로 다이어그램 중심 학습 노트 PDF 생성 |

## 설치

### ZIP / 일반 도구

원하는 플러그인 경로만 sparse checkout으로 받은 뒤, `skills/<스킬명>/` 폴더 전체를
ZIP으로 압축하거나 사용하는 도구의 skill 디렉터리에 복사한다.

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/lopahn2/naria-skills.git
cd naria-skills
git sparse-checkout set plugins/stt2study-note-pdf
```

실제 스킬 경로:

```text
plugins/stt2study-note-pdf/skills/stt2study-note-pdf/
```

### Claude Code / Cowork

Claude는 `main`을 Marketplace로 사용한다.

```bash
claude plugin marketplace add lopahn2/naria-skills --sparse .claude-plugin plugins
claude plugin install stt2study-note-pdf@naria-skills
```

업데이트:

```bash
claude plugin marketplace update naria-skills
claude plugin update stt2study-note-pdf@naria-skills
```

Claude Desktop/Cowork Marketplace UI에서는 `lopahn2/naria-skills`를 등록하고
`stt2study-note-pdf`를 설치한다. 별도 branch ref는 지정하지 않는다.

### ChatGPT Work / Codex

OpenAI Marketplace에는 `openai-marketplace` 브랜치를 등록한다.

```bash
codex plugin marketplace add lopahn2/naria-skills --ref openai-marketplace
codex plugin add stt2study-note-pdf@naria-skills
```

설치 또는 업데이트 뒤에는 새 대화를 시작해야 새 스킬 목록이 반영될 수 있다.

## 새 스킬 추가

```text
plugins/<plugin-name>/
├── marketplace.json
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        └── ... 나머지 파일
```

- 현재 `plugin-name`, `skill-name`, `SKILL.md`의 frontmatter `name`은 동일하게 관리한다.
- `plugins/<plugin-name>/marketplace.json`은 OpenAI 생성용 표시 정보이며 Claude가 읽지 않는다.
- 새 Claude 플러그인은 `.claude-plugin/marketplace.json`의 `plugins` 배열에도 추가한다.
- main에 push하면 `plugins/*/skills/*/SKILL.md`를 탐색해 `openai-marketplace`를 갱신한다.

## 원본 수정 규칙

- `main/plugins/**`만 수정한다.
- `openai-marketplace`에는 직접 커밋하지 않는다.
- 배포본은 symlink를 쓰지 않는다.

## 라이선스

[MIT](LICENSE)
