# OKF 변환 규칙

`dayNN`의 산출물 중 **②(중간 산출물)와 ③(입력 자료)만** OKF(Open Knowledge
Format) 문서로 만든다. **①(최종 PDF)과 ④(작업용 임시 파일)는 대상이 아니다.**

OKF는 구글 클라우드가 낸 가벼운 마크다운 규격이다. 필수 필드는 `type` 하나뿐이고,
`title`/`description`/`resource`/`tags`/`timestamp`가 선택 필드다. 파일 경로가
곧 개념 ID이고, 관계는 그냥 마크다운 링크로 표현한다.

## 왜 ②③만 올리는가

**나중에 이 산출물을 처음 보는 사람이 ②③만 가지고 ①(최종 통합본)을 다시
뽑을 수 있어야 한다.** 이게 OKF 변환의 전제 조건이다. 감사 결과:

- Phase B가 원문 없이 `notes/*.md`만으로 통합본을 쓰도록 이미 설계돼 있다 → ②만으로 충분
- 교본 매칭 결과(어느 교시가 어느 교재 몇 쪽인지)는 각 노트 헤더에 이미 박혀 있다
- 도해를 원본 쓸지/직접 그릴지 판단도 노트의 `## 교본 도해 판정` 표에 있다
- **도해 크롭 좌표만 예외였다** — `slide.py`가 이제 `dayNN/diagrams.json`에
  기록하므로 이것도 해결됐다. 눈대중으로 다시 잡을 필요 없다.

이 조건이 깨지는 변경을 하면(예: 노트 스펙에서 필드를 빼거나, 크롭 좌표
기록을 생략하면) OKF 변환 이전에 **원본 파이프라인부터 고쳐야 한다.**

## 디렉토리 구조

```
<project-root>/          # 예: ax-advanced/ (작업 폴더 이름, 사람이 부르는 이름과 같을 필요 없음)
  day01/ day02/ ...
  glossary.md
  okf/
    index.md             # 전체 색인 — build_okf.py 가 매번 재생성
    log.md               # 실행 이력 — append-only
    glossary.md           # glossary.md 미러 (OKF 프론트매터 얹음)
    day01/
      notes/pMM.md        # 노트 원문 복사 + 프론트매터
      sources/
        pMM-audio.md       # 포인터 → day01/audio/pMM.txt
        <name>-textbook.md # 포인터 → day01/slides/<name>.pdf
        idx-<name>.md      # 포인터 → day01/idx_<name>.json
      cross.md             # 포인터 → day01/cross.jsonl
      diagrams.md          # 포인터 → day01/diagrams.json (있으면)
```

`python3 $S/build_okf.py <project> dayNN` 로 하루치를 한 번에 만든다.
날짜가 늘어나면 그 dayNN만 다시 돌리면 된다 — 이미 만든 날짜는 안 건드린다
(단, `index.md`/`glossary.md` 미러는 매번 전체 재생성된다).

## type 목록

| type | 대상 | 내용 | resource |
|---|---|---|---|
| `lecture-note` | `notes/pMM.md` | 원문 그대로 복사 | (없음, 본문이 곧 내용) |
| `source-transcript` | `audio/pMM.txt` | 포인터만 | ✅ |
| `source-textbook` | `slides/*.pdf` | 포인터만 | ✅ |
| `textbook-index` | `idx_*.json` | 포인터만 | ✅ |
| `cross-index` | `cross.jsonl` | 포인터만 | ✅ |
| `diagram-crop-log` | `diagrams.json` | 포인터만 | ✅ |
| `glossary` | `glossary.md` | 원문 그대로 복사 | (없음) |
| `index` | `okf/index.md` 자기 자신 | 색인 | (없음) |

마크다운이 아닌 산출물은 **재작성하지 않고 포인터만 만든다** — 원본과 내용이
중복되면 나중에 둘 중 하나가 갱신 안 돼 어긋나는 지점이 생긴다.

## `project` 필드

`project`는 작업 폴더명이 아니라 **사람이 부르는 프로젝트 이름**이다
(예: `ax-advanced`). 모든 OKF 문서 프론트매터에 박아 둔다 — 나중에 여러
강의(프로젝트)의 `okf/` 트리를 한 지식베이스에 합쳐도 어느 프로젝트 소속인지
구분하기 위해서다.

- **지금 이 프로젝트는 `ax-advanced`다.**
- 이 플러그인을 다른 사람이 다른 강의에 쓸 때는 그 사람이 프로젝트 이름을
  알려준다. **묻지 않고 임의로 짓지 마라.**
- 이름이 없으면 `build_okf.py` 를 돌리기 전에 사용자에게 물어라.

## OpenViking(또는 다른 RAG 시스템)에 업로드할 때

**대상 프로젝트 네임스페이스가 원격에 이미 있는지 먼저 확인한다.** 없으면
바로 새로 만들지 말고, 사용자에게 "OpenViking에 `<project>`라는 프로젝트가
없는데, 이 이름으로 새로 만들어도 되나요?"라고 반드시 먼저 물어라. 오타나
다른 이름으로 잘못 올리면 지식베이스가 프로젝트별로 쪼개지는 걸 나중에
합칠 방법이 없다. 이미 있는 프로젝트면 그냥 그 아래에 이어서 올린다.
