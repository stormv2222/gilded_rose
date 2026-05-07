# Phase 2 설계 — 아이템 유형 판별 메서드 추출

## 목표

`update_quality` 내에 분산된 `item.name` 직접 비교식을 판별 메서드로 감싸
**비교의 의도**가 코드에 드러나도록 합니다.
코드 구조나 동작은 변경하지 않으며, 비교 표현만 메서드 호출로 교체합니다.

---

## 변경 대상 파일

- `gilded_rose.py`

---

## 현재 코드의 문제

Phase 1 이후 상수로 교체됐지만, 여전히 `item.name ==` / `item.name !=` 비교식이
`update_quality` 안에 **6곳** 분산되어 있습니다.
비교식만 봐서는 "이 아이템이 특정 유형인가?"라는 의도가 바로 드러나지 않습니다.

| 줄 | 현재 비교식 |
|----|-----------|
| 11 | `item.name != AGED_BRIE and item.name != BACKSTAGE_PASSES` |
| 14 | `item.name == BACKSTAGE_PASSES` |
| 21 | `item.name != SULFURAS` |
| 24 | `item.name != AGED_BRIE` |
| 25 | `item.name != BACKSTAGE_PASSES` |
| 27 | `item.name != SULFURAS` |

---

## 변경 내용

### 1. 판별 메서드 3개 추가

`GildedRose` 클래스에 아이템 유형을 판별하는 메서드를 추가합니다.

```python
def _is_aged_brie(self, item):
    return item.name == AGED_BRIE

def _is_sulfuras(self, item):
    return item.name == SULFURAS

def _is_backstage_passes(self, item):
    return item.name == BACKSTAGE_PASSES
```

### 2. `update_quality` 내 비교식 → 메서드 호출 교체

| Before | After |
|--------|-------|
| `item.name != AGED_BRIE and item.name != BACKSTAGE_PASSES` | `not self._is_aged_brie(item) and not self._is_backstage_passes(item)` |
| `item.name == BACKSTAGE_PASSES` | `self._is_backstage_passes(item)` |
| `item.name != SULFURAS` (sell_in 감소 전) | `not self._is_sulfuras(item)` |
| `item.name != AGED_BRIE` | `not self._is_aged_brie(item)` |
| `item.name != BACKSTAGE_PASSES` | `not self._is_backstage_passes(item)` |
| `item.name != SULFURAS` (quality 감소) | `not self._is_sulfuras(item)` |

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

    def update_quality(self):
        for item in self.items:
            if item.name != AGED_BRIE and item.name != BACKSTAGE_PASSES:
                if item.quality > 0:
                    if item.name != SULFURAS:
                        item.quality = item.quality - 1
            else:
                if item.quality < 50:
                    item.quality = item.quality + 1
                    if item.name == BACKSTAGE_PASSES:
                        if item.sell_in < 11:
                            if item.quality < 50:
                                item.quality = item.quality + 1
                        if item.sell_in < 6:
                            if item.quality < 50:
                                item.quality = item.quality + 1
            if item.name != SULFURAS:
                item.sell_in = item.sell_in - 1
            if item.sell_in < 0:
                if item.name != AGED_BRIE:
                    if item.name != BACKSTAGE_PASSES:
                        if item.quality > 0:
                            if item.name != SULFURAS:
                                item.quality = item.quality - 1
                    else:
                        item.quality = item.quality - item.quality
                else:
                    if item.quality < 50:
                        item.quality = item.quality + 1
```

**변경 후**
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

    def update_quality(self):
        for item in self.items:
            if not self._is_aged_brie(item) and not self._is_backstage_passes(item):
                if item.quality > 0:
                    if not self._is_sulfuras(item):
                        item.quality = item.quality - 1
            else:
                if item.quality < 50:
                    item.quality = item.quality + 1
                    if self._is_backstage_passes(item):
                        if item.sell_in < 11:
                            if item.quality < 50:
                                item.quality = item.quality + 1
                        if item.sell_in < 6:
                            if item.quality < 50:
                                item.quality = item.quality + 1
            if not self._is_sulfuras(item):
                item.sell_in = item.sell_in - 1
            if item.sell_in < 0:
                if not self._is_aged_brie(item):
                    if not self._is_backstage_passes(item):
                        if item.quality > 0:
                            if not self._is_sulfuras(item):
                                item.quality = item.quality - 1
                    else:
                        item.quality = item.quality - item.quality
                else:
                    if item.quality < 50:
                        item.quality = item.quality + 1
```

---

## 회귀 검증

```
pytest tests/ -v
```

동작 변경이 없으므로 기존 테스트 전체가 통과해야 합니다.
