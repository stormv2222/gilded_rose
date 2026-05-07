# Gilded Rose 유닛 테스트 작성 계획

---

## 1. 테스트 파일 구조

```
tests/
└── test_gilded_rose.py
```

테스트는 아이템 유형별로 클래스를 분리하고, 각 클래스 안에서 시나리오별 메서드를 작성합니다.

```python
class TestNormalItem:     # 일반 아이템
class TestAgedBrie:       # Aged Brie
class TestSulfuras:       # Sulfuras
class TestBackstagePasses: # Backstage passes
class TestQualityBounds:  # 공통 경계값 (0, 50)
```

---

## 2. 아이템별 테스트 케이스

### 2-1. 일반 아이템 (`TestNormalItem`)

| 테스트 메서드 | 시나리오 | 초기값 | 기대값 |
|--------------|---------|--------|--------|
| `test_quality_decreases_by_1` | 하루 지남, 기한 내 | SellIn=5, Quality=10 | Quality=9 |
| `test_sellin_decreases_by_1` | SellIn 감소 확인 | SellIn=5, Quality=10 | SellIn=4 |
| `test_quality_decreases_by_2_after_sellin` | SellIn 지난 후 | SellIn=0, Quality=10 | Quality=8 |
| `test_quality_never_negative` | Quality가 0일 때 | SellIn=5, Quality=0 | Quality=0 |
| `test_quality_never_negative_after_sellin` | SellIn 지난 후 Quality=1 | SellIn=0, Quality=1 | Quality=0 |

---

### 2-2. Aged Brie (`TestAgedBrie`)

| 테스트 메서드 | 시나리오 | 초기값 | 기대값 |
|--------------|---------|--------|--------|
| `test_quality_increases_by_1` | 하루 지남, 기한 내 | SellIn=5, Quality=10 | Quality=11 |
| `test_sellin_decreases_by_1` | SellIn 감소 확인 | SellIn=5, Quality=10 | SellIn=4 |
| `test_quality_increases_by_2_after_sellin` | SellIn 지난 후 | SellIn=0, Quality=10 | Quality=12 |
| `test_quality_capped_at_50` | Quality가 50일 때 | SellIn=5, Quality=50 | Quality=50 |
| `test_quality_capped_at_50_after_sellin` | SellIn 지난 후 Quality=49 | SellIn=0, Quality=49 | Quality=50 (51 아님) |

---

### 2-3. Sulfuras (`TestSulfuras`)

| 테스트 메서드 | 시나리오 | 초기값 | 기대값 |
|--------------|---------|--------|--------|
| `test_quality_never_changes` | 하루 지남 | SellIn=5, Quality=80 | Quality=80 |
| `test_sellin_never_changes` | SellIn 불변 | SellIn=5, Quality=80 | SellIn=5 |

---

### 2-4. Backstage passes (`TestBackstagePasses`)

| 테스트 메서드 | 시나리오 | 초기값 | 기대값 |
|--------------|---------|--------|--------|
| `test_quality_increases_by_1_over_10` | SellIn > 10 | SellIn=11, Quality=10 | Quality=11 |
| `test_quality_increases_by_2_at_10` | SellIn = 10 (경계) | SellIn=10, Quality=10 | Quality=12 |
| `test_quality_increases_by_2_between_6_and_10` | 6 <= SellIn <= 10 | SellIn=7, Quality=10 | Quality=12 |
| `test_quality_increases_by_3_at_5` | SellIn = 5 (경계) | SellIn=5, Quality=10 | Quality=13 |
| `test_quality_increases_by_3_between_1_and_5` | 1 <= SellIn <= 5 | SellIn=3, Quality=10 | Quality=13 |
| `test_quality_drops_to_0_after_concert` | SellIn = 0 이후 | SellIn=0, Quality=30 | Quality=0 |
| `test_quality_capped_at_50` | Quality 상한 | SellIn=5, Quality=49 | Quality=50 (52 아님) |

---

### 2-5. 공통 경계값 (`TestQualityBounds`)

| 테스트 메서드 | 시나리오 |
|--------------|---------|
| `test_quality_minimum_is_0` | 어떤 아이템도 Quality < 0 불가 |
| `test_quality_maximum_is_50` | Sulfuras 제외 Quality > 50 불가 |

---

## 3. 경계값 기준 정리

SPEC에서 경계가 모호한 조건을 명확히 해석합니다.

| 조건 | 해석 | 근거 |
|------|------|------|
| Backstage passes `SellIn <= 10` | update 후 SellIn 기준이 아닌 **update 전 SellIn** 기준 | 코드에서 `sell_in < 11` 체크 후 `sell_in -= 1` |
| Backstage passes `SellIn <= 0` | 콘서트 당일(SellIn=0) update 후 Quality=0 | `sell_in < 0` 조건은 SellIn 감소 후 체크 |
| 일반 아이템 기한 초과 | SellIn이 0에서 -1이 된 시점부터 2씩 감소 | 동일한 순서 |

---

## 4. 테스트 작성 순서

1. `TestNormalItem` — 기본 동작 검증
2. `TestAgedBrie` — Quality 역방향 변동
3. `TestSulfuras` — 불변 검증
4. `TestBackstagePasses` — 단계별 Quality 증가 + 초기화
5. `TestQualityBounds` — 공통 제약 교차 검증

---

## 5. 테스트 코드 스켈레톤

```python
import unittest
from gilded_rose import GildedRose, Item


def make_item(name, sell_in, quality):
    return Item(name, sell_in, quality)

def update(item):
    GildedRose([item]).update_quality()
    return item


class TestNormalItem(unittest.TestCase):
    NAME = "normal item"

    def test_quality_decreases_by_1(self): ...
    def test_sellin_decreases_by_1(self): ...
    def test_quality_decreases_by_2_after_sellin(self): ...
    def test_quality_never_negative(self): ...
    def test_quality_never_negative_after_sellin(self): ...


class TestAgedBrie(unittest.TestCase):
    NAME = "Aged Brie"

    def test_quality_increases_by_1(self): ...
    def test_sellin_decreases_by_1(self): ...
    def test_quality_increases_by_2_after_sellin(self): ...
    def test_quality_capped_at_50(self): ...
    def test_quality_capped_at_50_after_sellin(self): ...


class TestSulfuras(unittest.TestCase):
    NAME = "Sulfuras, Hand of Ragnaros"

    def test_quality_never_changes(self): ...
    def test_sellin_never_changes(self): ...


class TestBackstagePasses(unittest.TestCase):
    NAME = "Backstage passes to a TAFKAL80ETC concert"

    def test_quality_increases_by_1_over_10(self): ...
    def test_quality_increases_by_2_at_10(self): ...
    def test_quality_increases_by_2_between_6_and_10(self): ...
    def test_quality_increases_by_3_at_5(self): ...
    def test_quality_increases_by_3_between_1_and_5(self): ...
    def test_quality_drops_to_0_after_concert(self): ...
    def test_quality_capped_at_50(self): ...


class TestQualityBounds(unittest.TestCase):

    def test_quality_minimum_is_0(self): ...
    def test_quality_maximum_is_50(self): ...


if __name__ == "__main__":
    unittest.main()
```
