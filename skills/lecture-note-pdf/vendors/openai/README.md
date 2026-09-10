# 강의 노트 PDF 생성 (OpenAI / Codex)

이 폴더는 ChatGPT Work/Codex용 플러그인 루트다. 실제 스킬 지침은
[`skills/lecture-note-pdf/SKILL.md`](skills/lecture-note-pdf/SKILL.md)에 있다.

공통 원칙·스크립트·참고 문서는 스킬 루트의 원본을 심볼릭 링크로 공유한다.
따라서 OpenAI 실행 방식만 바꿀 때는 이 폴더의 `.codex-plugin/`과 `skills/`만 수정한다.

## 구성

```
vendors/openai/
├── .codex-plugin/plugin.json    Codex 플러그인 매니페스트
├── skills/lecture-note-pdf/
│   ├── SKILL.md                 Codex 오케스트레이션 지침
│   ├── PRINCIPLES.md -> ../../../../PRINCIPLES.md
│   ├── scripts/ -> ../../../../scripts
│   ├── references/ -> ../../../../references
│   └── assets/ -> ../../../../assets
└── README.md                    이 파일
```

## 실행 모델

- Phase A(map): 교시마다 Codex 서브에이전트를 띄워 `notes/pMM.md`만 작성하게 한다.
- Phase B2(reduce): 완성된 노트를 파트별로 나누어 서브에이전트가 `partN.html`을 쓴다.
- 메인 오케스트레이터는 원문·파트 본문을 대화 컨텍스트에 복사하지 않고, 파일을 통해서만
  다음 단계를 연결한다.
- 기본 서브에이전트 모델 표기는 Claude Sonnet 대신 `gpt-5.6-terra`를 사용한다. 런타임에서
  해당 모델을 선택할 수 없으면, 사용자에게 특정 모델 사용을 허가받고 파일 출력·짧은 반환 규칙은 유지한다.

`dayNN/cross.jsonl`은 병렬 작업이 동시에 접근할 수 있으므로 반드시
`scripts/append_cross.py`를 통해서만 추가한다. 세부 프롬프트와 단계별 제약은
[`skills/lecture-note-pdf/SKILL.md`](skills/lecture-note-pdf/SKILL.md)를 따른다.
