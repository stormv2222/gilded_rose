# Phase 4 — TestBackstagePasses (백스테이지 패스)

## 목표

콘서트 날짜가 다가올수록 Quality가 단계적으로 증가하고,
콘서트 종료(SellIn=0 → -1) 후에는 Quality가 0이 됨을 검증합니다.

---

## 테스트 케이스

| # | 메서드 | 시나리오 | 초기값 | 기대값 |
|---|--------|---------|--------|--------|
| 1 | `test_quality_increases_by_1_over_10` | SellIn > 10 구간 | SellIn=11, Quality=10 | Quality=11 |
| 2 | `test_quality_increases_by_2_at_10` | SellIn=10 경계값 | SellIn=10, Quality=10 | Quality=12 |
| 3 | `test_quality_increases_by_2_between_6_and_10` | 6 ≤ SellIn ≤ 10 중간값 | SellIn=7, Quality=10 | Quality=12 |
| 4 | `test_quality_increases_by_3_at_5` | SellIn=5 경계값 | SellIn=5, Quality=10 | Quality=13 |
| 5 | `test_quality_increases_by_3_between_1_and_5` | 1 ≤ SellIn ≤ 5 중간값 | SellIn=3, Quality=10 | Quality=13 |
| 6 | `test_quality_drops_to_0_after_concert` | SellIn=0, 콘서트 당일 → 종료 | SellIn=0, Quality=30 | Quality=0 |
| 7 | `test_quality_capped_at_50` | 상한 경계: SellIn=5, Quality=49 → +3 시도 | SellIn=5, Quality=49 | Quality=50 |

---

## 경계값 주의사항

**핵심: 조건 체크 순서**

현재 구현 코드는 Quality를 변경한 **뒤** SellIn을 감소시킵니다.
즉, Quality 증가 구간 판단은 update **전** SellIn 값을 기준으로 합니다.

```
[코드 실행 순서]
1. Quality 변경 (sell_in < 11 또는 sell_in < 6 체크)
2. sell_in -= 1
3. sell_in < 0 이면 Quality 후처리
```

| SellIn 초기값 | 판단 기준 | 증가량 | update 후 SellIn |
|-------------|---------|--------|-----------------|
| 11 | sell_in < 11? No | +1 | 10 |
| 10 | sell_in < 11? Yes | +2 | 9 |
| 5 | sell_in < 6? Yes | +3 | 4 |
| 0 | sell_in < 0? No → SellIn 감소 → -1 → Quality=0 | 0 | -1 |

- `test_quality_capped_at_50`: SellIn=5이면 +3 적용 시도, Quality=49이므로 50에서 멈춰야 합니다.

---

## 구현 코드

```python
class TestBackstagePasses(unittest.TestCase):
    NAME = "Backstage passes to a TAFKAL80ETC concert"

    def test_quality_increases_by_1_over_10(self):
        item = update(Item(self.NAME, 11, 10))
        self.assertEqual(item.quality, 11)

    def test_quality_increases_by_2_at_10(self):
        item = update(Item(self.NAME, 10, 10))
        self.assertEqual(item.quality, 12)

    def test_quality_increases_by_2_between_6_and_10(self):
        item = update(Item(self.NAME, 7, 10))
        self.assertEqual(item.quality, 12)

    def test_quality_increases_by_3_at_5(self):
        item = update(Item(self.NAME, 5, 10))
        self.assertEqual(item.quality, 13)

    def test_quality_increases_by_3_between_1_and_5(self):
        item = update(Item(self.NAME, 3, 10))
        self.assertEqual(item.quality, 13)

    def test_quality_drops_to_0_after_concert(self):
        item = update(Item(self.NAME, 0, 30))
        self.assertEqual(item.quality, 0)

    def test_quality_capped_at_50(self):
        item = update(Item(self.NAME, 5, 49))
        self.assertEqual(item.quality, 50)
```

---

## 검증 포인트

- [ ] SellIn > 10 구간에서 Quality가 +1 증가하는가
- [ ] SellIn = 10 경계에서 Quality가 +2 증가하는가
- [ ] SellIn = 5 경계에서 Quality가 +3 증가하는가
- [ ] SellIn = 0 update 후 Quality가 0이 되는가
- [ ] Quality가 50 상한을 초과하지 않는가
