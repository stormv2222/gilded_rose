# Phase 4 설계 — Quality 경계값 보정 메서드 추출

## 목표

각 업데이트 메서드에 분산된 `if quality < 50` / `if quality > 0` 인라인 경계 가드를
`_clamp_quality` 메서드로 통합합니다.
각 메서드는 경계를 신경 쓰지 않고 증감만 수행하고, 마지막에 `_clamp_quality`로 보정합니다.

---

## 변경 대상 파일

- `gilded_rose.py`

---

## 현재 코드의 문제

Phase 3 이후 각 업데이트 메서드에 `if quality < 50`, `if quality > 0` 가드가 인라인으로 남아 있습니다.
경계 처리 방식이 메서드마다 분산되어 일관성을 파악하기 어렵습니다.

| 메서드 | 인라인 경계 가드 |
|--------|---------------|
| `_update_normal_item` | `if item.quality > 0` (×2) |
| `_update_aged_brie` | `if item.quality < 50` (×2) |
| `_update_backstage_passes` | `if item.quality < 50` (×3) |

---

## 변경 내용

### 1. `_clamp_quality` 추가

Quality를 0 이상 50 이하로 보정합니다.

```python
def _clamp_quality(self, item):
    item.quality = max(0, min(50, item.quality))
```

### 2. 각 메서드에서 인라인 경계 가드 제거 후 `_clamp_quality` 호출

경계 가드 없이 증감을 수행하고 마지막에 `_clamp_quality`로 일괄 보정합니다.

---

## 메서드별 변경 전/후

### `_update_normal_item`

**변경 전**
```python
def _update_normal_item(self, item):
    item.sell_in = item.sell_in - 1
    if item.quality > 0:
        item.quality = item.quality - 1
    if item.sell_in < 0 and item.quality > 0:
        item.quality = item.quality - 1
```

**변경 후**
```python
def _update_normal_item(self, item):
    item.sell_in = item.sell_in - 1
    item.quality = item.quality - 1
    if item.sell_in < 0:
        item.quality = item.quality - 1
    self._clamp_quality(item)
```

**동작 검증**

| SellIn | Quality | -1 후 | 기한 초과 -1 | clamp | 결과 |
|--------|---------|-------|------------|-------|------|
| 5 | 10 | 9 | — | 9 | 9 |
| 0 | 10 | 9 | 8 | 8 | 8 |
| 5 | 0 | -1 | — | 0 | 0 |
| 0 | 1 | 0 | -1 | 0 | 0 |

---

### `_update_aged_brie`

**변경 전**
```python
def _update_aged_brie(self, item):
    item.sell_in = item.sell_in - 1
    if item.quality < 50:
        item.quality = item.quality + 1
    if item.sell_in < 0 and item.quality < 50:
        item.quality = item.quality + 1
```

**변경 후**
```python
def _update_aged_brie(self, item):
    item.sell_in = item.sell_in - 1
    item.quality = item.quality + 1
    if item.sell_in < 0:
        item.quality = item.quality + 1
    self._clamp_quality(item)
```

**동작 검증**

| SellIn | Quality | +1 후 | 기한 초과 +1 | clamp | 결과 |
|--------|---------|-------|------------|-------|------|
| 5 | 10 | 11 | — | 11 | 11 |
| 0 | 10 | 11 | 12 | 12 | 12 |
| 5 | 50 | 51 | — | 50 | 50 |
| 0 | 49 | 50 | 51 | 50 | 50 |

---

### `_update_backstage_passes`

**변경 전**
```python
def _update_backstage_passes(self, item):
    item.sell_in = item.sell_in - 1
    if item.sell_in < 0:
        item.quality = 0
        return
    if item.quality < 50:
        item.quality = item.quality + 1
    if item.sell_in < 10 and item.quality < 50:
        item.quality = item.quality + 1
    if item.sell_in < 5 and item.quality < 50:
        item.quality = item.quality + 1
```

**변경 후**
```python
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

**동작 검증**

| SellIn(전) | sell_in 감소 후 | Quality | +1 | < 10 +1 | < 5 +1 | clamp | 결과 |
|-----------|----------------|---------|-----|--------|-------|-------|------|
| 11 | 10 | 10 | 11 | — | — | 11 | 11 |
| 10 | 9 | 10 | 11 | 12 | — | 12 | 12 |
| 5 | 4 | 10 | 11 | 12 | 13 | 13 | 13 |
| 0 | -1 | 30 | (0으로 초기화 후 return) | — | — | — | 0 |
| 5 | 4 | 49 | 50 | 51 | 52 | 50 | 50 |

---

## 변경 후 전체 코드

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

---

## 회귀 검증

```
pytest tests/ -v
```

동작 변경이 없으므로 기존 테스트 전체가 통과해야 합니다.
