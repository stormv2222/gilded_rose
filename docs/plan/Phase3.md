# Phase 3 — TestSulfuras (전설 아이템)

## 목표

Sulfuras는 전설의 아이템으로 `SellIn`과 `Quality` 모두 **절대 변하지 않음**을 검증합니다.
다양한 초기값에서도 불변성이 유지되는지 확인합니다.

---

## 테스트 케이스

| # | 메서드 | 시나리오 | 초기값 | 기대값 |
|---|--------|---------|--------|--------|
| 1 | `test_quality_never_changes` | 하루 경과 후 Quality 불변 | SellIn=5, Quality=80 | Quality=80 |
| 2 | `test_sellin_never_changes` | 하루 경과 후 SellIn 불변 | SellIn=5, Quality=80 | SellIn=5 |
| 3 | `test_quality_never_changes_when_sellin_negative` | SellIn이 음수여도 Quality 불변 | SellIn=-1, Quality=80 | Quality=80 |

---

## 경계값 주의사항

- Sulfuras의 Quality는 80으로 고정되어 있으며, 50 상한 제약이 **적용되지 않습니다**.
- SellIn이 음수인 경우에도 어떤 변경도 일어나지 않아야 합니다.
- 이 아이템만이 Quality > 50을 합법적으로 가질 수 있습니다.

---

## 구현 코드

```python
class TestSulfuras(unittest.TestCase):
    NAME = "Sulfuras, Hand of Ragnaros"

    def test_quality_never_changes(self):
        item = update(Item(self.NAME, 5, 80))
        self.assertEqual(item.quality, 80)

    def test_sellin_never_changes(self):
        item = update(Item(self.NAME, 5, 80))
        self.assertEqual(item.sell_in, 5)

    def test_quality_never_changes_when_sellin_negative(self):
        item = update(Item(self.NAME, -1, 80))
        self.assertEqual(item.quality, 80)
```

---

## 검증 포인트

- [ ] 하루가 지나도 Quality가 변하지 않는가
- [ ] 하루가 지나도 SellIn이 변하지 않는가
- [ ] SellIn이 이미 음수여도 불변성이 유지되는가
