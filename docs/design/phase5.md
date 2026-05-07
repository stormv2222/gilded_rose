# Phase 5 설계 — 연산자 및 표현 정리

## 목표

각 업데이트 메서드에 남아있는 `item.x = item.x + 1` 형태의 표현을
복합 대입 연산자(`+=`, `-=`)로 교체하여 의도를 간결하게 표현합니다.
동작은 변경하지 않으며, 표현만 정리합니다.

---

## 변경 대상 파일

- `gilded_rose.py`

---

## 현재 코드의 문제

Phase 4 이후에도 증감 표현이 장황하게 남아 있습니다.

```python
item.sell_in = item.sell_in - 1  # -= 1 로 축약 가능
item.quality = item.quality - 1  # -= 1 로 축약 가능
item.quality = item.quality + 1  # += 1 로 축약 가능
```

---

## 교체 목록

| 위치 | Before | After |
|------|--------|-------|
| `_update_normal_item` | `item.sell_in = item.sell_in - 1` | `item.sell_in -= 1` |
| `_update_normal_item` | `item.quality = item.quality - 1` | `item.quality -= 1` |
| `_update_normal_item` (기한 초과) | `item.quality = item.quality - 1` | `item.quality -= 1` |
| `_update_aged_brie` | `item.sell_in = item.sell_in - 1` | `item.sell_in -= 1` |
| `_update_aged_brie` | `item.quality = item.quality + 1` | `item.quality += 1` |
| `_update_aged_brie` (기한 초과) | `item.quality = item.quality + 1` | `item.quality += 1` |
| `_update_backstage_passes` | `item.sell_in = item.sell_in - 1` | `item.sell_in -= 1` |
| `_update_backstage_passes` | `item.quality = item.quality + 1` | `item.quality += 1` |
| `_update_backstage_passes` (sell_in < 10) | `item.quality = item.quality + 1` | `item.quality += 1` |
| `_update_backstage_passes` (sell_in < 5) | `item.quality = item.quality + 1` | `item.quality += 1` |

총 **10곳** 교체

---

## 변경 전/후 전체 코드

**변경 전**
```python
    def _update_normal_item(self, item):
        item.sell_in = item.sell_in - 1
        item.quality = item.quality - 1
        if item.sell_in < 0:
            item.quality = item.quality - 1
        self._clamp_quality(item)

    def _update_aged_brie(self, item):
        item.sell_in = item.sell_in - 1
        item.quality = item.quality + 1
        if item.sell_in < 0:
            item.quality = item.quality + 1
        self._clamp_quality(item)

    def _update_backstage_passes(self, item):
        item.sell_in = item.sell_in - 1
        if item.sell_in < 0:
            item.quality = 0
            return
        item.quality = item.quality + 1
        if item.sell_in < 10:
            item.quality = item.quality + 1
        if item.sell_in < 5:
            item.quality = item.quality + 1
        self._clamp_quality(item)
```

**변경 후**
```python
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
```

---

## 최종 전체 코드

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

---

## 회귀 검증

```
pytest tests/ -v
```

동작 변경이 없으므로 기존 테스트 전체가 통과해야 합니다.
