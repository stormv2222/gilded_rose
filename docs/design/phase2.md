# Phase 2 설계 — 아이템별 Updater 클래스 구현

## 목표

`GildedRose._update_*` 메서드의 로직을 `ItemUpdater`를 상속한 독립 클래스로 이동합니다.
`GildedRose`는 이 단계에서 변경하지 않으며, 기존 메서드와 새 클래스가 병존합니다.

---

## 변경 대상 파일

- `gilded_rose.py`

---

## 구현할 클래스 목록

| 클래스 | 대응 아이템 | 로직 출처 |
|--------|-----------|---------|
| `NormalItemUpdater` | 일반 아이템 | `GildedRose._update_normal_item` |
| `AgedBrieUpdater` | Aged Brie | `GildedRose._update_aged_brie` |
| `SulfurasUpdater` | Sulfuras | `GildedRose.update_quality` 내 `continue` |
| `BackstagePassesUpdater` | Backstage passes | `GildedRose._update_backstage_passes` |

---

## 각 클래스 구현

### `NormalItemUpdater`

```
규칙: 하루 -1, 기한 초과 후 추가 -1 (총 -2), 하한 0
```

```python
class NormalItemUpdater(ItemUpdater):
    def update(self, item):
        item.sell_in -= 1
        item.quality -= 1
        if item.sell_in < 0:
            item.quality -= 1
        self._clamp_quality(item)
```

### `AgedBrieUpdater`

```
규칙: 하루 +1, 기한 초과 후 추가 +1 (총 +2), 상한 50
```

```python
class AgedBrieUpdater(ItemUpdater):
    def update(self, item):
        item.sell_in -= 1
        item.quality += 1
        if item.sell_in < 0:
            item.quality += 1
        self._clamp_quality(item)
```

### `SulfurasUpdater`

```
규칙: SellIn·Quality 모두 불변
```

```python
class SulfurasUpdater(ItemUpdater):
    def update(self, item):
        pass
```

### `BackstagePassesUpdater`

```
규칙: sell_in > 10 → +1 / ≤ 10 → +2 / ≤ 5 → +3 / 기한 초과 → 0
```

```python
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

---

## 변경 전/후 전체 코드

**변경 전**
```python
from abc import ABC, abstractmethod

AGED_BRIE = "Aged Brie"
SULFURAS = "Sulfuras, Hand of Ragnaros"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"


class ItemUpdater(ABC):
    @abstractmethod
    def update(self, item):
        pass

    def _clamp_quality(self, item):
        item.quality = max(0, min(50, item.quality))


class GildedRose(object):
    # ... 기존 코드 유지 (변경 없음)
```

**변경 후**
```python
from abc import ABC, abstractmethod

AGED_BRIE = "Aged Brie"
SULFURAS = "Sulfuras, Hand of Ragnaros"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"


class ItemUpdater(ABC):
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


class AgedBrieUpdater(ItemUpdater):
    def update(self, item):
        item.sell_in -= 1
        item.quality += 1
        if item.sell_in < 0:
            item.quality += 1
        self._clamp_quality(item)


class SulfurasUpdater(ItemUpdater):
    def update(self, item):
        pass


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


class GildedRose(object):
    # ... 기존 코드 유지 (변경 없음)
```

---

## 변경 요약

| 항목 | 내용 |
|------|------|
| 추가 | `NormalItemUpdater`, `AgedBrieUpdater`, `SulfurasUpdater`, `BackstagePassesUpdater` 4개 클래스 |
| 유지 | `GildedRose` 전체 (변경 없음) |
| 유지 | `Item` 클래스 (변경 없음) |

---

## 회귀 검증

```
pytest tests/ -v
```

`GildedRose`를 변경하지 않으므로 기존 테스트 전체가 통과해야 합니다.
