# Phase 3 설계 — 아이템별 업데이트 메서드 분리

## 목표

`update_quality` 안에 혼재된 4종 아이템의 규칙 로직을 각각 독립 메서드로 추출합니다.
`update_quality`는 유형 분기만 담당하고, 실제 규칙은 각 메서드에 위임합니다.

---

## 변경 대상 파일

- `gilded_rose.py`

---

## 현재 코드의 문제

Phase 2 이후에도 `update_quality` 한 메서드가 아래 두 가지를 동시에 담당합니다.

1. 아이템 유형 분기
2. 유형별 Quality/SellIn 갱신 규칙

그 결과 중첩이 최대 5단계에 달하며, 특정 아이템의 규칙만 파악하려면 메서드 전체를 읽어야 합니다.

---

## 핵심 설계 결정 — SellIn 감소 시점 이동

현재 코드는 아래 순서로 동작합니다.

```
① Quality 1차 변경  (sell_in 감소 전 기준으로 조건 체크)
② sell_in -= 1
③ Quality 2차 변경  (sell_in < 0 여부로 기한 초과 처리)
```

메서드를 분리하면 각 메서드 안에서 `sell_in`을 먼저 감소시킨 뒤 조건을 체크합니다.
감소 전 기준이던 임계값이 감소 후 기준으로 1씩 조정됩니다.

| 항목 | 원본 (감소 전 기준) | 분리 후 (감소 후 기준) |
|------|----------------|------------------|
| Backstage passes +2 구간 | `sell_in < 11` | `sell_in < 10` |
| Backstage passes +3 구간 | `sell_in < 6` | `sell_in < 5` |
| 기한 초과 판단 | `sell_in < 0` | `sell_in < 0` (동일) |

---

## 변경 내용

### 1. `update_quality` — 분기만 담당

```python
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
```

### 2. `_update_normal_item`

```
규칙: 하루 -1, 기한 초과 후 추가 -1 (총 -2)
```

```python
def _update_normal_item(self, item):
    item.sell_in = item.sell_in - 1
    if item.quality > 0:
        item.quality = item.quality - 1
    if item.sell_in < 0 and item.quality > 0:
        item.quality = item.quality - 1
```

**동작 검증**

| SellIn | Quality | sell_in 감소 후 | 1차 -1 | 기한 초과 -1 | 결과 |
|--------|---------|----------------|--------|------------|------|
| 5 | 10 | 4 | 9 | — | 9 |
| 0 | 10 | -1 | 9 | 8 | 8 |
| 0 | 1 | -1 | 0 | (0이라 skip) | 0 |
| 5 | 0 | 4 | (0이라 skip) | — | 0 |

### 3. `_update_aged_brie`

```
규칙: 하루 +1, 기한 초과 후 추가 +1 (총 +2), 상한 50
```

```python
def _update_aged_brie(self, item):
    item.sell_in = item.sell_in - 1
    if item.quality < 50:
        item.quality = item.quality + 1
    if item.sell_in < 0 and item.quality < 50:
        item.quality = item.quality + 1
```

**동작 검증**

| SellIn | Quality | sell_in 감소 후 | 1차 +1 | 기한 초과 +1 | 결과 |
|--------|---------|----------------|--------|------------|------|
| 5 | 10 | 4 | 11 | — | 11 |
| 0 | 10 | -1 | 11 | 12 | 12 |
| 0 | 49 | -1 | 50 | (50이라 skip) | 50 |
| 5 | 50 | 4 | (50이라 skip) | — | 50 |

### 4. `_update_backstage_passes`

```
규칙: sell_in > 10 → +1 / 5 < sell_in ≤ 10 → +2 / 0 < sell_in ≤ 5 → +3 / sell_in ≤ 0 → 0
```

sell_in을 먼저 감소시킨 뒤 조건을 체크하므로 임계값이 1씩 낮아집니다.

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

**동작 검증**

| SellIn(전) | sell_in 감소 후 | 적용 규칙 | Quality(전) | 결과 |
|-----------|----------------|---------|------------|------|
| 11 | 10 | +1 (10 < 10 false) | 10 | 11 |
| 10 | 9 | +2 (9 < 10 true) | 10 | 12 |
| 5 | 4 | +3 (4 < 5 true) | 10 | 13 |
| 0 | -1 | 0으로 초기화 | 30 | 0 |
| 5 | 4 | +3 시도, 상한 50 | 49 | 50 |

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
        if item.quality > 0:
            item.quality = item.quality - 1
        if item.sell_in < 0 and item.quality > 0:
            item.quality = item.quality - 1

    def _update_aged_brie(self, item):
        item.sell_in = item.sell_in - 1
        if item.quality < 50:
            item.quality = item.quality + 1
        if item.sell_in < 0 and item.quality < 50:
            item.quality = item.quality + 1

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

---

## 회귀 검증

```
pytest tests/ -v
```

동작 변경이 없으므로 기존 테스트 전체가 통과해야 합니다.
이 단계가 핵심 리팩토링이므로 테스트 실패 시 임계값 조정 여부를 먼저 점검합니다.
