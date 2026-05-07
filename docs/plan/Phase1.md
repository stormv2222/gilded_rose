# Phase 1 — TestNormalItem (일반 아이템)

## 목표

일반 아이템의 기본 동작(Quality 감소, SellIn 감소, 기한 초과 패널티, 하한 제약)을 검증합니다.

---

## 테스트 케이스

| # | 메서드 | 시나리오 | 초기값 | 기대값 |
|---|--------|---------|--------|--------|
| 1 | `test_quality_decreases_by_1` | 기한 내, 하루 경과 | SellIn=5, Quality=10 | Quality=9 |
| 2 | `test_sellin_decreases_by_1` | SellIn 감소 확인 | SellIn=5, Quality=10 | SellIn=4 |
| 3 | `test_quality_decreases_by_2_after_sellin` | SellIn=0 → update 후 SellIn=-1, Quality -2 | SellIn=0, Quality=10 | Quality=8 |
| 4 | `test_quality_never_negative` | Quality=0 상태에서 update | SellIn=5, Quality=0 | Quality=0 |
| 5 | `test_quality_never_negative_after_sellin` | SellIn 초과 후 Quality=1 → -2 시도 | SellIn=0, Quality=1 | Quality=0 |

---

## 경계값 주의사항

- `test_quality_decreases_by_2_after_sellin`: 초기 `SellIn=0`으로 설정하면 update 후 `SellIn=-1`이 되어 "기한 초과" 조건에 진입합니다.
- `test_quality_never_negative_after_sellin`: 기한 초과 시 -2가 적용되려 해도 Quality=1이므로 0이 되어야 하며, -1이 되어서는 안 됩니다.

---

## 구현 코드

```python
import unittest
from gilded_rose import GildedRose, Item


def update(item):
    GildedRose([item]).update_quality()
    return item


class TestNormalItem(unittest.TestCase):
    NAME = "normal item"

    def test_quality_decreases_by_1(self):
        item = update(Item(self.NAME, 5, 10))
        self.assertEqual(item.quality, 9)

    def test_sellin_decreases_by_1(self):
        item = update(Item(self.NAME, 5, 10))
        self.assertEqual(item.sell_in, 4)

    def test_quality_decreases_by_2_after_sellin(self):
        item = update(Item(self.NAME, 0, 10))
        self.assertEqual(item.quality, 8)

    def test_quality_never_negative(self):
        item = update(Item(self.NAME, 5, 0))
        self.assertEqual(item.quality, 0)

    def test_quality_never_negative_after_sellin(self):
        item = update(Item(self.NAME, 0, 1))
        self.assertEqual(item.quality, 0)
```

---

## 검증 포인트

- [ ] Quality가 하루에 정확히 1씩 감소하는가
- [ ] SellIn이 하루에 정확히 1씩 감소하는가
- [ ] SellIn 기한 초과 후 Quality가 2씩 감소하는가
- [ ] Quality가 0 미만으로 내려가지 않는가
