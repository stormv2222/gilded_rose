# Phase 1 설계 — ItemUpdater 추상 기반 클래스 정의

## 목표

모든 아이템 updater가 따를 공통 인터페이스(`update`)와
공유 유틸(`_clamp_quality`)을 추상 기반 클래스로 정의합니다.
기존 `GildedRose` 코드는 변경하지 않습니다.

---

## 변경 대상 파일

- `gilded_rose.py`

---

## 변경 내용

### 추가: `ItemUpdater` 추상 기반 클래스

`abc` 모듈의 `ABC`, `abstractmethod`를 사용하여 정의합니다.

| 구성 요소 | 종류 | 역할 |
|----------|------|------|
| `update(item)` | 추상 메서드 | 각 updater가 반드시 구현해야 할 규칙 진입점 |
| `_clamp_quality(item)` | 일반 메서드 | Quality 0 이상 50 이하 보정 (모든 updater 공유) |

```python
from abc import ABC, abstractmethod

class ItemUpdater(ABC):
    @abstractmethod
    def update(self, item):
        pass

    def _clamp_quality(self, item):
        item.quality = max(0, min(50, item.quality))
```

---

## 변경 전/후 전체 코드

**변경 전**
```python
AGED_BRIE = "Aged Brie"
SULFURAS = "Sulfuras, Hand of Ragnaros"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"


class GildedRose(object):
    def __init__(self, items):
        self.items = items

    def _is_aged_brie(self, item):
        return item.name == AGED_BRIE

    def _is_sulfuras(self, item):
        return item.name == SULFURAS

    def _is_backstage_passes(self, item):
        return item.name == BACKSTAGE_PASSES

    def _clamp_quality(self, item):
        item.quality = max(0, min(50, item.quality))

    def update_quality(self):
        for item in self.items:
            if self._is_sulfuras(item):
                continue
            elif self._is_aged_brie(item):
                self._update_aged_brie(item)
            elif self._is_backstage_passes(item):
                self._update_backstage_passes(item)
            else:
                self._update_normal_item(item)

    def _update_normal_item(self, item):
        item.sell_in -= 1
        item.quality -= 1
        if item.sell_in < 0:
            item.quality -= 1
        self._clamp_quality(item)

    def _update_aged_brie(self, item):
        item.sell_in -= 1
        item.quality += 1
        if item.sell_in < 0:
            item.quality += 1
        self._clamp_quality(item)

    def _update_backstage_passes(self, item):
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


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
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


class GildedRose(object):
    def __init__(self, items):
        self.items = items

    def _is_aged_brie(self, item):
        return item.name == AGED_BRIE

    def _is_sulfuras(self, item):
        return item.name == SULFURAS

    def _is_backstage_passes(self, item):
        return item.name == BACKSTAGE_PASSES

    def _clamp_quality(self, item):
        item.quality = max(0, min(50, item.quality))

    def update_quality(self):
        for item in self.items:
            if self._is_sulfuras(item):
                continue
            elif self._is_aged_brie(item):
                self._update_aged_brie(item)
            elif self._is_backstage_passes(item):
                self._update_backstage_passes(item)
            else:
                self._update_normal_item(item)

    def _update_normal_item(self, item):
        item.sell_in -= 1
        item.quality -= 1
        if item.sell_in < 0:
            item.quality -= 1
        self._clamp_quality(item)

    def _update_aged_brie(self, item):
        item.sell_in -= 1
        item.quality += 1
        if item.sell_in < 0:
            item.quality += 1
        self._clamp_quality(item)

    def _update_backstage_passes(self, item):
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
| 추가 | `from abc import ABC, abstractmethod` import |
| 추가 | `ItemUpdater` 추상 클래스 (`update` 추상 메서드 + `_clamp_quality`) |
| 유지 | `GildedRose` 전체 (변경 없음) |
| 유지 | `Item` 클래스 (변경 없음) |

---

## 회귀 검증

```
pytest tests/ -v
```

`GildedRose`를 변경하지 않으므로 기존 테스트 전체가 통과해야 합니다.
