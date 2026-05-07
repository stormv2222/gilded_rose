# Phase 3 설계 — GildedRose 레지스트리 연결 및 기존 코드 제거

## 목표

`__init_subclass__`를 활용한 자동 등록 방식으로 레지스트리를 `ItemUpdater` 내부에 캡슐화합니다.
새 아이템 추가 시 `GildedRose`를 포함한 **기존 코드를 전혀 수정하지 않아도** 됩니다.

---

## 기존 Phase 3 방식의 문제

```python
class GildedRose(object):
    _updaters = {
        AGED_BRIE: AgedBrieUpdater(),       # 새 아이템마다
        SULFURAS: SulfurasUpdater(),         # 이 딕셔너리를
        BACKSTAGE_PASSES: BackstagePassesUpdater(),  # 수정해야 함 → OCP 위반
    }
```

새 아이템 추가 시 `GildedRose._updaters`를 수정해야 하므로 OCP를 위반합니다.

---

## 해결 방법 — `__init_subclass__` 자동 등록

Python의 `__init_subclass__`를 활용하면 서브클래스가 **정의되는 시점에 자동으로 레지스트리에 등록**됩니다.
`GildedRose`는 레지스트리를 읽기만 하며, 새 아이템을 추가해도 절대 수정할 필요가 없습니다.

---

## 변경 대상 파일

- `gilded_rose.py`

---

## 변경 내용

### 1. `ItemUpdater` — `__init_subclass__` 및 `for_item` 추가

```python
class ItemUpdater(ABC):
    _registry: dict = {}

    def __init_subclass__(cls, item_name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if item_name:
            ItemUpdater._registry[item_name] = cls()

    @classmethod
    def for_item(cls, item):
        return cls._registry.get(item.name, NormalItemUpdater())

    @abstractmethod
    def update(self, item):
        pass

    def _clamp_quality(self, item):
        item.quality = max(0, min(50, item.quality))
```

| 추가 요소 | 역할 |
|----------|------|
| `_registry` | 이름 → updater 인스턴스 매핑 (클래스 변수) |
| `__init_subclass__` | 서브클래스 정의 시 `item_name` 키워드가 있으면 자동 등록 |
| `for_item(item)` | 아이템 이름으로 updater 조회, 없으면 `NormalItemUpdater` 반환 |

### 2. 각 Updater 클래스 — `item_name` 키워드 추가

클래스 정의 시 `item_name=` 키워드를 선언하는 것만으로 자동 등록됩니다.

```python
class NormalItemUpdater(ItemUpdater):           # item_name 없음 → 기본값으로 사용
    def update(self, item): ...

class AgedBrieUpdater(ItemUpdater, item_name=AGED_BRIE):
    def update(self, item): ...

class SulfurasUpdater(ItemUpdater, item_name=SULFURAS):
    def update(self, item): ...

class BackstagePassesUpdater(ItemUpdater, item_name=BACKSTAGE_PASSES):
    def update(self, item): ...
```

### 3. `GildedRose` — 레지스트리 연결 및 기존 메서드 제거

```python
class GildedRose(object):
    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            ItemUpdater.for_item(item).update(item)
```

제거 대상 메서드 7개:

| 제거 메서드 | 이유 |
|------------|------|
| `_is_aged_brie` | 레지스트리 조회로 대체 |
| `_is_sulfuras` | 레지스트리 조회로 대체 |
| `_is_backstage_passes` | 레지스트리 조회로 대체 |
| `_update_normal_item` | `NormalItemUpdater.update`로 이동 완료 |
| `_update_aged_brie` | `AgedBrieUpdater.update`로 이동 완료 |
| `_update_backstage_passes` | `BackstagePassesUpdater.update`로 이동 완료 |
| `_clamp_quality` | `ItemUpdater._clamp_quality`로 이동 완료 |

---

## 새 아이템 추가 방법 (완료 후)

`GildedRose`를 포함한 기존 코드 수정 없이 클래스 하나만 추가합니다.

```python
class ConjuredUpdater(ItemUpdater, item_name="Conjured Mana Cake"):
    def update(self, item):
        item.sell_in -= 1
        item.quality -= 2
        if item.sell_in < 0:
            item.quality -= 2
        self._clamp_quality(item)
```

---

## 최종 전체 코드

```python
from abc import ABC, abstractmethod

AGED_BRIE = "Aged Brie"
SULFURAS = "Sulfuras, Hand of Ragnaros"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"


class ItemUpdater(ABC):
    _registry: dict = {}

    def __init_subclass__(cls, item_name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if item_name:
            ItemUpdater._registry[item_name] = cls()

    @classmethod
    def for_item(cls, item):
        return cls._registry.get(item.name, NormalItemUpdater())

    @abstractmethod
    def update(self, item):
        pass

    def _clamp_quality(self, item):
        item.quality = max(0, min(50, item.quality))


class NormalItemUpdater(ItemUpdater):
    def update(self, item):
        item.sell_in -= 1
        item.quality -= 1
        if item.sell_in < 0:
            item.quality -= 1
        self._clamp_quality(item)


class AgedBrieUpdater(ItemUpdater, item_name=AGED_BRIE):
    def update(self, item):
        item.sell_in -= 1
        item.quality += 1
        if item.sell_in < 0:
            item.quality += 1
        self._clamp_quality(item)


class SulfurasUpdater(ItemUpdater, item_name=SULFURAS):
    def update(self, item):
        pass


class BackstagePassesUpdater(ItemUpdater, item_name=BACKSTAGE_PASSES):
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


class GildedRose(object):
    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            ItemUpdater.for_item(item).update(item)


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
```

---

## 변경 요약

| 항목 | 내용 |
|------|------|
| `ItemUpdater` 변경 | `_registry`, `__init_subclass__`, `for_item` 추가 |
| Updater 클래스 변경 | 클래스 선언에 `item_name=` 키워드 추가 |
| `GildedRose` 변경 | 기존 메서드 7개 제거, `update_quality` 1줄로 교체 |
| OCP 준수 | 새 아이템 추가 시 기존 코드 수정 불필요 |

---

## 회귀 검증

```
pytest tests/ -v
```

`update_quality` 동작이 교체되는 핵심 단계이므로 테스트 결과를 집중 확인합니다.
