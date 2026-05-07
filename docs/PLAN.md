# 클래스 단위 확장 리팩토링 계획

---

## 1. 현재 구조의 문제

가독성 리팩토링(Phase 1~5) 이후 `GildedRose`는 아래 구조를 갖습니다.

```
GildedRose
├── update_quality()        ← 유형 분기 (if/elif 체인)
├── _is_aged_brie()
├── _is_sulfuras()
├── _is_backstage_passes()
├── _update_normal_item()
├── _update_aged_brie()
├── _update_backstage_passes()
└── _clamp_quality()
```

**문제**: 새 아이템을 추가하려면 `GildedRose` 내부를 직접 수정해야 합니다.
- `update_quality`에 분기 추가
- `_update_*` 메서드 추가

이는 **OCP(개방-폐쇄 원칙) 위반**입니다.

---

## 2. 목표 구조

아이템 유형별 규칙을 독립 클래스로 분리하고, `GildedRose`는 레지스트리를 통해 위임합니다.
새 아이템 추가 시 **기존 코드를 수정하지 않고** 새 클래스만 추가하면 됩니다.

```
ItemUpdater (추상 기반 클래스)
├── update(item)            ← 추상 메서드 (아이템 유형별로 구현)
└── _clamp_quality(item)    ← 공통 유틸

NormalItemUpdater(ItemUpdater)
AgedBrieUpdater(ItemUpdater)
SulfurasUpdater(ItemUpdater)
BackstagePassesUpdater(ItemUpdater)

GildedRose
├── _updaters               ← {이름: updater 인스턴스} 레지스트리
├── _default_updater        ← NormalItemUpdater (미등록 아이템 기본값)
└── update_quality()        ← 레지스트리에서 updater 조회 후 위임
```

---

## 3. 새 아이템 추가 방법 (목표 상태)

```python
class ConjuredUpdater(ItemUpdater):
    def update(self, item):
        item.sell_in -= 1
        item.quality -= 2
        if item.sell_in < 0:
            item.quality -= 2
        self._clamp_quality(item)
```

`GildedRose`나 다른 updater를 수정할 필요 없이 클래스만 추가합니다.

---

## 4. 리팩토링 Phase

### Phase 1 — ItemUpdater 추상 기반 클래스 정의

**목표**: 모든 updater가 따를 공통 인터페이스와 공유 유틸을 정의합니다.

**작업**
- `abc.ABC`를 상속한 `ItemUpdater` 추상 클래스 추가
- `update(item)` 추상 메서드 선언
- `_clamp_quality(item)` 공통 메서드 정의

**변경 후 코드**
```python
from abc import ABC, abstractmethod

class ItemUpdater(ABC):
    @abstractmethod
    def update(self, item):
        pass

    def _clamp_quality(self, item):
        item.quality = max(0, min(50, item.quality))
```

**기존 코드 변경**: 없음 (`GildedRose` 유지)
**회귀 검증**: `pytest tests/ -v` — 전체 통과 확인

---

### Phase 2 — 아이템별 Updater 클래스 구현

**목표**: 각 아이템 유형의 규칙을 독립 클래스로 구현합니다.

**작업**
- `NormalItemUpdater`, `AgedBrieUpdater`, `SulfurasUpdater`, `BackstagePassesUpdater` 구현
- 로직은 `GildedRose._update_*` 메서드에서 이동

**변경 후 코드**
```python
class NormalItemUpdater(ItemUpdater):
    def update(self, item):
        item.sell_in -= 1
        item.quality -= 1
        if item.sell_in < 0:
            item.quality -= 1
        self._clamp_quality(item)

class AgedBrieUpdater(ItemUpdater):
    def update(self, item):
        item.sell_in -= 1
        item.quality += 1
        if item.sell_in < 0:
            item.quality += 1
        self._clamp_quality(item)

class SulfurasUpdater(ItemUpdater):
    def update(self, item):
        pass  # 불변 아이템 — 아무것도 하지 않음

class BackstagePassesUpdater(ItemUpdater):
    def update(self, item):
        item.sell_in -= 1
        if item.sell_in < 0:
            item.quality = 0
            return
        item.quality += 1
        if item.sell_in < 10:
            item.quality += 1
        if item.sell_in < 5:
            item.quality += 1
        self._clamp_quality(item)
```

**기존 코드 변경**: 없음 (`GildedRose` 유지)
**회귀 검증**: `pytest tests/ -v` — 전체 통과 확인

---

### Phase 3 — GildedRose 레지스트리 연결 및 기존 코드 제거

**목표**: `GildedRose`가 레지스트리를 통해 updater에 위임하도록 변경합니다.
기존의 `_is_*`, `_update_*`, `_clamp_quality` 메서드를 모두 제거합니다.

**작업**
- `GildedRose`에 `_updaters` 레지스트리 추가
- `update_quality`를 레지스트리 조회 + 위임 방식으로 교체
- 기존 `_is_*`, `_update_*`, `_clamp_quality` 메서드 제거

**변경 후 코드**
```python
class GildedRose(object):
    _updaters = {
        AGED_BRIE: AgedBrieUpdater(),
        SULFURAS: SulfurasUpdater(),
        BACKSTAGE_PASSES: BackstagePassesUpdater(),
    }
    _default_updater = NormalItemUpdater()

    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            updater = self._updaters.get(item.name, self._default_updater)
            updater.update(item)
```

**기존 코드 변경**: `GildedRose` 전면 교체
**회귀 검증**: `pytest tests/ -v` — 전체 통과 확인 (핵심 단계)

---

## 5. Phase별 진행 순서

| Phase | 작업 | 기존 코드 변경 | 비고 |
|-------|------|-------------|------|
| 1 | `ItemUpdater` 추상 기반 클래스 정의 | 없음 | 인터페이스만 추가 |
| 2 | 아이템별 Updater 클래스 4개 구현 | 없음 | 기존 메서드와 병존 |
| 3 | `GildedRose` 레지스트리 연결 + 기존 메서드 제거 | `GildedRose` 전면 교체 | 핵심 단계, 회귀 집중 확인 |

---

## 6. 회귀 검증

각 Phase 완료 후 아래 명령으로 검증합니다.

```
pytest tests/ -v
pytest tests/ --cov
```
