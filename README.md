# naria-skills

naria가 만든 AI 에이전트 스킬 모음이다. **사람이 수정하는 canonical 원본은 항상
`main` 브랜치의 `skills/<이름>/`뿐**이다.

## 배포 방식

| 사용 환경 | 사용할 브랜치/경로 |
| --- | --- |
| 마켓플레이스를 지원하지 않는 도구 | `main`의 `skills/<스킬 이름>/`을 ZIP으로 내려받아 압축을 풀고 폴더 전체를 사용 |
| ChatGPT Work / Codex | `openai-marketplace` 브랜치 |
| Claude Code / Cowork | `claude-marketplace` 브랜치 |

OpenAI와 Claude 브랜치는 자동 생성된 배포 산출물이다. 직접 수정하지 않는다.
`main`에 스킬 원본을 변경하면 GitHub Actions가 두 브랜치를 실제 파일 복사본으로 다시
만들고, 각 브랜치의 `SOURCE.json`에 생성 기준 main 커밋 SHA를 남긴다.

## 스킬 목록

| 스킬 | 설명 |
| --- | --- |
| [`stt2study-note-pdf`](skills/stt2study-note-pdf/) | 강의 녹취록(STT)과 교재 PDF로 다이어그램 중심 학습 노트 PDF 생성 |

## 설치

### ZIP / 일반 도구

`main` 브랜치에서 `skills/stt2study-note-pdf/` 폴더를 내려받아 압축을 풀고,
그 폴더 전체를 사용하는 도구의 skill 디렉터리에 복사한다. 마켓플레이스가 없는
환경에서는 이것이 정식 배포 경로다.

### ChatGPT Work / Codex

마켓플레이스 소스로 이 저장소의 **`openai-marketplace` 브랜치**를 선택한다.

```bash
codex plugin marketplace add lopahn2/naria-skills --ref openai-marketplace
codex plugin add stt2study-note-pdf@naria-skills
```

설치 또는 업데이트 뒤에는 새 대화를 시작해야 새 스킬 목록이 반영될 수 있다.

### Claude Code / Cowork

마켓플레이스 소스로 이 저장소의 **`claude-marketplace` 브랜치**를 선택하고
`stt2study-note-pdf` 플러그인을 설치한다. 사용하는 Claude Code 버전의
Marketplace UI/CLI에서 source ref를 `claude-marketplace`로 지정한다.

## 원본 수정 규칙

- `main/skills/**`만 수정한다.
- `openai-marketplace`, `claude-marketplace`에는 직접 커밋하지 않는다.
- 배포본은 symlink를 쓰지 않는다. Windows, sparse checkout, Codex 설치 캐시에서도
  안전하도록 실제 파일 복사본으로 생성한다.

## 라이선스

[MIT](LICENSE)
