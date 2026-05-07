# Gilded Rose 프로젝트

## 프로젝트 개요

Gilded Rose 리팩토링 카타입니다.
가독성 리팩토링(Phase 1~5)이 완료된 상태에서,
새로운 아이템 유형을 클래스 단위로 추가할 수 있도록 확장 가능한 구조로 리팩토링하는 것이 현재 목표입니다.

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
│   └── SPEC.md           # 아이템별 요구사항 명세
└── tests/                # 테스트 파일
```

---

새 아이템 추가 시 `update_quality`의 분기와 `_update_*` 메서드를 동시에 수정해야 하므로
**OCP(개방-폐쇄 원칙)를 위반**합니다.

---

## 다음 리팩토링 목표 — 클래스 단위 확장 구조

아이템 유형별 규칙을 **독립 클래스**로 분리하여,
새 아이템 추가 시 기존 코드를 수정하지 않고 클래스만 추가하면 되는 구조로 개선합니다.

---

## 아이템 종류

| 아이템 | 규칙 요약 |
|--------|---------|
| 일반 아이템 | Quality 매일 -1, 기한 초과 시 -2 |
| `Aged Brie` | Quality 매일 +1, 기한 초과 시 +2 |
| `Sulfuras, Hand of Ragnaros` | SellIn·Quality 불변 |
| `Backstage passes to a TAFKAL80ETC concert` | SellIn에 따라 +1/+2/+3, 콘서트 후 Quality=0 |

Quality 범위: 0 이상 50 이하 (Sulfuras 제외)

---

## 테스트 실행

```bash
# 전체 테스트
pytest tests/ -v
pytest tests/ --cov
```

---

## 브랜치 현황

| 브랜치 | 내용 |
|--------|------|
| `main` | 초기 구현 + SPEC.md |
| `branch1` | 테스트 계획 및 Phase별 unittest 추가 |
| `branch2` | 가독성 리팩토링 Phase 1~5 완료 |
| `branch3` | 설계 문서 정리, 클래스 단위 확장 리팩토링 진행 예정 |

---

## 개발 규칙

- 리팩토링 완료 후 반드시 `pytest tests/ -v` 로 회귀 검증
- `Item` 클래스는 수정 금지 (레거시 제약)
- 동작 변경 없이 구조만 개선
- 새 아이템 추가 시 기존 클래스 수정 없이 새 클래스 추가만으로 가능해야 함
