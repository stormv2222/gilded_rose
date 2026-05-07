# Phase 2 — TestAgedBrie (숙성 치즈)

## 목표

Aged Brie는 시간이 지날수록 Quality가 **증가**하는 특수 아이템입니다.
기한 내/초과 시의 증가량 차이와 Quality 상한(50)을 검증합니다.

---

## 테스트 케이스

| # | 메서드 | 시나리오 | 초기값 | 기대값 |
|---|--------|---------|--------|--------|
| 1 | `test_quality_increases_by_1` | 기한 내, 하루 경과 | SellIn=5, Quality=10 | Quality=11 |
| 2 | `test_sellin_decreases_by_1` | SellIn 감소 확인 (Aged Brie도 SellIn은 감소) | SellIn=5, Quality=10 | SellIn=4 |
| 3 | `test_quality_increases_by_2_after_sellin` | SellIn=0 → update 후 SellIn=-1, Quality +2 | SellIn=0, Quality=10 | Quality=12 |
| 4 | `test_quality_capped_at_50` | Quality=50 상태에서 update | SellIn=5, Quality=50 | Quality=50 |
| 5 | `test_quality_capped_at_50_after_sellin` | SellIn 초과 후 Quality=49 → +2 시도 | SellIn=0, Quality=49 | Quality=50 |

---

## 경계값 주의사항

- `test_quality_capped_at_50_after_sellin`: 기한 초과 시 +2가 적용되려 해도 Quality=49이므로 50에서 멈춰야 합니다. 51이 되어서는 안 됩니다.
- `test_quality_increases_by_2_after_sellin`: 초기 `SellIn=0`으로 설정하면 update 후 `SellIn=-1`이 되어 "기한 초과" 조건에 진입합니다.

---

## 구현 코드

```python
class TestAgedBrie(unittest.TestCase):
    NAME = "Aged Brie"

    def test_quality_increases_by_1(self):
        item = update(Item(self.NAME, 5, 10))
        self.assertEqual(item.quality, 11)

    def test_sellin_decreases_by_1(self):
        item = update(Item(self.NAME, 5, 10))
        self.assertEqual(item.sell_in, 4)

    def test_quality_increases_by_2_after_sellin(self):
        item = update(Item(self.NAME, 0, 10))
        self.assertEqual(item.quality, 12)

    def test_quality_capped_at_50(self):
        item = update(Item(self.NAME, 5, 50))
        self.assertEqual(item.quality, 50)

    def test_quality_capped_at_50_after_sellin(self):
        item = update(Item(self.NAME, 0, 49))
        self.assertEqual(item.quality, 50)
```

---

## 검증 포인트

- [ ] 기한 내 Quality가 하루에 정확히 1씩 증가하는가
- [ ] 기한 초과 후 Quality가 2씩 증가하는가
- [ ] Quality가 50을 초과하지 않는가
- [ ] SellIn은 여전히 1씩 감소하는가
