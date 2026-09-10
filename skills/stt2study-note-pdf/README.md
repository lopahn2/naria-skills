# stt2study-note-pdf

강의 녹취록(STT)과 교재 PDF로 **다이어그램 중심 학습 노트 PDF**를 만드는 스킬.

## 무엇을 하는가

교시별 녹취와 교재를 넣으면 하루치 통합 학습 노트를 PDF로 만든다.
녹취를 요약하는 것이 아니라 **재구성**한다 — 강사의 비유와 현장 사례를
살리고, 개념을 다이어그램으로 바꾸고, 언급된 기술마다 학습 지도를 남긴다.

```
dayNN/
  slides/   교재 PDF (여러 개, 교시 구분 없어도 됨)
  audio/    p01.txt p02.txt ... (교시별 녹취, 인코딩 무관)
        ↓
  out/dayNN.pdf   35~45쪽 통합 노트
```

전체 흐름(Phase 0~D, OKF 변환 포함)을 그림으로 보려면
`assets/pipeline-diagram.html`을 브라우저로 열어본다.

## 어떤 도구를 쓰든 먼저 읽을 것

**[`PRINCIPLES.md`](PRINCIPLES.md)** — 4대 원칙, 아키텍처, Phase 0~D의 판단 기준
(등급, 매칭 임계값, 분량 기준, 사용자에게 확인할 것)이 전부 여기 있다. 벤더 무관.

## SKILL.md 하나, 벤더는 패키징만 다르다

이 스킬은 **`SKILL.md` 원본이 하나뿐이다.** Claude Code용/Codex용 지침이 서로
다른 파일로 따로 존재하지 않는다 — `SKILL.md` 안에서 "지금 어떤 환경인지"를
판별해 그 분기를 따르도록 지시돼 있다 (모델 지정처럼 벤더별로 다른 값이 필요한
부분만 분기, 나머지는 공통).

| 마켓플레이스 | 패키징 위치 |
|---|---|
| Claude Code / Cowork | [`../../marketplace/claude/stt2study-note-pdf/`](../../marketplace/claude/stt2study-note-pdf/) — 이 스킬 원본을 심볼릭 링크로 참조, `agents/*.md`(Task 서브에이전트 정의)만 실체로 존재 |
| Codex / ChatGPT Work | [`../../marketplace/codex/stt2study-note-pdf/`](../../marketplace/codex/stt2study-note-pdf/) — 심볼릭 링크 불가라 빌드 시 원본을 그대로 복사(`tools/build_codex_package.py`, CI 자동 실행). **여기는 손으로 고치지 않는다** |
| 서브에이전트를 지원하지 않는 도구 | [`generic-usage.md`](generic-usage.md) — 마켓플레이스에 올리지 않는 순수 참고 문서, 한 세션이 순차로 수행 |

**내용을 고칠 땐 항상 이 스킬 원본(`SKILL.md`, `PRINCIPLES.md`, `scripts/`,
`references/`, `assets/`)만 고친다.** `marketplace/claude/`는 심볼릭 링크라
원본을 고치면 자동으로 따라오고, `marketplace/codex/`는 CI가 push마다 원본과
다시 맞춘다 — 두 곳 다 직접 편집 대상이 아니다.

## 자동으로 처리되는 것

- **폰트 사전 체크** — `prep.py` 실행 맨 앞에서 한글 폰트(Noto Sans CJK KR) 유무를
  확인하고, 없으면 비용이 큰 단계(교시별 분석, 파트 작성) 전에 즉시 중단한다
- **인코딩** — UTF-16BE/LE, CP949 자동 감지 후 UTF-8 정규화
- **교본 매칭** — 교시마다 교본이 다를 수 있음을 전제로 교시×교본 행렬 판정
  (regex가 아니라 고정 기술어 목록에 대한 단순 문자열 카운트)
- **OCR 판정** — 텍스트 레이어 유무에 따라 A/B/C 등급, C는 사용자에게 먼저 고지.
  OCR 자체는 자동 실행되지 않고, 매칭 보조용으로만 필요할 때 수동으로 돌린다
- **STT 교정** — 누적 사전 기반. `프라엔지니어링 → 프롬프트 엔지니어링` 등
- **다이어그램** — 원본이 도해면 잘라 쓰고, 텍스트면 인라인 SVG로 직접 그림.
  이 판단은 인덱스가 아니라 실제로 페이지를 렌더해서 본 시점(Phase A)에 내려진다
- **검증** — 컨택트 시트 + 이상 여백 자동 감지

## 산출물 등급과 OKF 변환

| 등급 | 예 | RAG(OKF) 대상 |
|---|---|---|
| ① 최종 | `out/dayNN.pdf` | ❌ |
| ② 중간 산출물(재사용/누적) | `notes/pMM.md`, `cross.jsonl`, `outline.md`, `idx_*.json`, `idx_*.summary.jsonl`, `diagrams.json`, `glossary.md` | ✅ |
| ③ 입력 자료(원본) | `audio/*.txt`, `slides/*.pdf` | ✅ |
| ④ 작업용 임시 파일 | `part*.html`, base64 캐시, 컨택트 시트 | ❌ |

②③만으로 ①을 다시 만들 수 있어야 한다는 게 이 구분의 전제다.
`python3 scripts/build_okf.py <project> dayNN`로 [OKF](https://okf.md/spec/) 문서로 감싼다.
자세한 type 목록과 디렉토리 구조는 `references/okf-spec.md` 참조.

## 구성

```
stt2study-note-pdf/
├── README.md                     이 파일
├── PRINCIPLES.md                 벤더 중립 원칙 — 모든 도구가 공통으로 따르는 방법론
├── scripts/                      벤더 무관 파이썬 스크립트
│   ├── prep.py                   폰트 체크 + 인코딩 정규화 + 인덱싱 + 등급 판정
│   ├── idx_summary.py            페이지별 "한 줄 요약" 룩업 jsonl 생성
│   ├── match.py                  교시×교본 매칭 행렬
│   ├── append_cross.py           dayNN/cross.jsonl 에 한 줄 append (동시쓰기 안전)
│   ├── slide.py                  원본 도해 추출 → base64 (+ diagrams.json 기록)
│   ├── build.py                  파트 조립 + 치환 + PDF 렌더
│   ├── verify.py                 컨택트 시트 + 여백 감지
│   └── build_okf.py              ②③ → OKF 문서 변환 (okf/dayNN/)
├── references/                   벤더 무관 참고문서
│   ├── chapter-note-spec.md      교시 노트 형식 (Phase A 출력 스펙)
│   ├── diagram-rules.md          혼합 규칙 · SVG 작성법 · 색 팔레트
│   ├── stt-corrections.md        누적 교정 사전
│   ├── document-structure.md     문서 구성 · 박스 사용법 · 분량 기준
│   └── okf-spec.md               OKF 변환 규칙 · type 목록 · 프로젝트 이름 규칙
├── assets/
│   ├── template.css              A4 인쇄 CSS (한글)
│   └── pipeline-diagram.html     전체 아키텍처 다이어그램
├── SKILL.md                      실행 지침 — Claude/Codex 분기 포함한 유일한 원본
└── generic-usage.md              서브에이전트 없는 도구용 순차 실행판 (마켓플레이스 패키징 아님)
```

마켓플레이스 패키징(`marketplace/claude/stt2study-note-pdf/`,
`marketplace/codex/stt2study-note-pdf/`)은 이 폴더 밖, 레포 루트의 `marketplace/`
아래에 있다 — 구조는 루트 [`README.md`](../../README.md) 참조.

`references/stt-corrections.md`는 회차가 쌓일수록 누적된다. 새 변이형을 발견하면
그 파일에 추가한다.

## 요구 사항

| 항목 | 비고 |
|---|---|
| Python | `chardet`, `pdfplumber`, `Pillow`, `playwright` — 없으면 자동 설치 |
| poppler-utils | `pdftoppm` (슬라이드 렌더링) |
| Chromium | HTML → PDF. 환경에 있는 것을 자동 탐색 |
| Noto Sans CJK KR | 한글 폰트. `fc-list :lang=ko`로 확인 — `prep.py`가 자동 체크 |
| tesseract-ocr-kor | 교재에 텍스트 레이어가 없을 때만 |

## 만들어진 배경

AX 고급과정 1일차(8교시 · 약 5시간 · 녹취 13만 자)를 실제로 처리하며 얻은 규칙을
정리한 것이다. 다음 실패들이 규칙으로 굳어 있다.

- 교재가 오전/오후로 다른데 하나로 매칭하려다 "다른 강의 자료"로 오판
- 구어체 녹취의 고빈도어가 전부 "이제/그래서/근데"라 빈도 대조가 무의미
- 원본 도해를 다시 그리다 표현 축 2개를 통째로 잃음
- 절 중간의 하드 페이지 브레이크로 반쯤 빈 페이지 발생
- 하루치를 단일 컨텍스트에서 처리하다 문서 작성 중 압축 발생
