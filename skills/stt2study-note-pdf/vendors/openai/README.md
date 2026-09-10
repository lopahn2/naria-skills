# 강의 노트 PDF 생성 (OpenAI / Codex 계열)

> TODO: ChatGPT/Codex 등 GPT 계열 모델이 이 스킬을 다루게 되면,
> 이 섹션을 그 모델 자신이 자기 서브에이전트 호출 문법에 맞게 채울 것.
>
> 채워야 할 것:
> - `../../PRINCIPLES.md`의 Phase A(map)를 어떻게 교시별 서브에이전트/서브프로세스
>   위임으로 옮길지 (Codex는 서브에이전트 호출이 실질적으로 가능함 — 순차든 병렬이든
>   그 시점에 지원하는 방식대로)
> - Phase B2(reduce)의 파트별 위임도 동일
> - 반환/응답은 짧게 제한할 것 (노트·파트 본문을 오케스트레이터 컨텍스트에 올리지 않기 위함)
> - `dayNN/cross.jsonl`은 반드시 `../../scripts/append_cross.py`로만 append할 것
>   (병렬 위임 시 동시쓰기 안전)
> - 노트 파일 스펙은 `../../references/chapter-note-spec.md`를 그대로 따를 것
> - 이 폴더 안에 실제 실행 방법(호출 문법, 프롬프트 템플릿)을 이 README를 대체하며 채울 것
>
> **이 폴더(`vendors/openai/`)만 고칠 것.** `../claude/`, `../generic/`은 다른
> 벤더용이니 참고는 해도 내용을 바꾸지 않는다. 공통 방법론(`../../PRINCIPLES.md`,
> `../../scripts/`, `../../references/`)을 고칠 땐 다른 벤더의 실행 방식과
> 어긋나지 않는지 확인하고, 애매하면 사용자에게 먼저 묻는다.

원칙(4대 원칙, Phase 0~D, 등급·매칭 기준, 산출물 구분)은 전부
[`../../PRINCIPLES.md`](../../PRINCIPLES.md)에 있다. 이 파일은 아직 비어 있다.
