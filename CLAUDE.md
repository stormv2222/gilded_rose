# Gilded Rose 프로젝트

## 프로젝트 개요

Gilded Rose 리팩토링 카타입니다.
레거시 코드(`gilded_rose.py`)의 동작을 유지하면서 가독성을 높이는 리팩토링을 목표로 합니다.

- GitHub: https://github.com/stormv2222/gilded_rose
- 언어: Python
- 테스트: pytest + unittest

---

## 디렉토리 구조

```
Refactoring/
├── gilded_rose.py        # 핵심 비즈니스 로직 (리팩토링 대상)
├── pytest.ini            # pytest 설정
├── CLAUDE.md
├── docs/
│   ├── SPEC.md           # 아이템별 요구사항 명세
│   └── PLAN.md           # 리팩토링 계획 (Phase 1~5)
└── tests/                # test 코드 위치
```

---

## 핵심 파일

### `gilded_rose.py`

`GildedRose` 클래스와 `Item` 클래스를 포함합니다.
`GildedRose.update_quality()`가 매일 모든 아이템의 `SellIn`, `Quality`를 갱신합니다.

### `docs/SPEC.md`

아이템 유형별 규칙 명세입니다. 리팩토링 중 동작 판단 기준으로 사용합니다.

### `docs/PLAN.md`

가독성 향상을 위한 리팩토링 계획입니다.

---

## 개발 규칙

- 리팩토링 시 각 Phase 완료 후 반드시 `pytest tests/ -v` 로 회귀 검증
- `Item` 클래스는 수정 금지 (레거시 제약)
- 동작 변경 없이 구조·가독성만 개선
