# Phase 1 설계 — 아이템 이름 상수화

## 목표

`gilded_rose.py` 전체에 하드코딩된 아이템 이름 문자열을 모듈 수준 상수로 추출합니다.
코드 구조나 동작은 변경하지 않으며, 문자열 리터럴만 상수 참조로 교체합니다.

---

## 변경 대상 파일

- `gilded_rose.py`

---

## 현재 코드의 문제

아이템 이름 문자열이 `update_quality` 메서드 안에 총 **6곳**에 분산되어 있습니다.

| 위치 (줄) | 문자열 |
|----------|--------|
| 7 | `"Aged Brie"` |
| 7 | `"Backstage passes to a TAFKAL80ETC concert"` |
| 9 | `"Sulfuras, Hand of Ragnaros"` |
| 14 | `"Backstage passes to a TAFKAL80ETC concert"` |
| 21 | `"Sulfuras, Hand of Ragnaros"` |
| 24 | `"Aged Brie"` |
| 25 | `"Backstage passes to a TAFKAL80ETC concert"` |
| 27 | `"Sulfuras, Hand of Ragnaros"` |

오탈자가 생기면 해당 조건만 조용히 실패하며, 수정 시 누락 가능성이 있습니다.

---

## 변경 내용

### 1. 모듈 상수 추가 (파일 최상단)

```python
AGED_BRIE = "Aged Brie"
SULFURAS = "Sulfuras, Hand of Ragnaros"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"
```

### 2. 문자열 리터럴 → 상수 교체

**변경 전**
```python
class GildedRose(object):
    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            if item.name != "Aged Brie" and item.name != "Backstage passes to a TAFKAL80ETC concert":
                if item.quality > 0:
                    if item.name != "Sulfuras, Hand of Ragnaros":
                        item.quality = item.quality - 1
            else:
                if item.quality < 50:
                    item.quality = item.quality + 1
                    if item.name == "Backstage passes to a TAFKAL80ETC concert":
                        if item.sell_in < 11:
                            if item.quality < 50:
                                item.quality = item.quality + 1
                        if item.sell_in < 6:
                            if item.quality < 50:
                                item.quality = item.quality + 1
            if item.name != "Sulfuras, Hand of Ragnaros":
                item.sell_in = item.sell_in - 1
            if item.sell_in < 0:
                if item.name != "Aged Brie":
                    if item.name != "Backstage passes to a TAFKAL80ETC concert":
                        if item.quality > 0:
                            if item.name != "Sulfuras, Hand of Ragnaros":
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

---

## 교체 목록

| Before | After |
|--------|-------|
| `"Aged Brie"` | `AGED_BRIE` |
| `"Sulfuras, Hand of Ragnaros"` | `SULFURAS` |
| `"Backstage passes to a TAFKAL80ETC concert"` | `BACKSTAGE_PASSES` |

---

## 회귀 검증

```
pytest tests/ -v
```

동작 변경이 없으므로 기존 테스트 전체가 통과해야 합니다.
