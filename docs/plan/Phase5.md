# Phase 5 — TestQualityBounds (공통 경계값)

## 목표

모든 아이템 유형에 걸쳐 적용되는 공통 제약을 교차 검증합니다.

- Quality는 절대 **0 미만**이 될 수 없습니다.
- Quality는 절대 **50 초과**가 될 수 없습니다. (Sulfuras 제외)

---

## 테스트 케이스

### `test_quality_minimum_is_0` — 하한 검증

Quality가 0인 상태에서 update해도 음수가 되지 않음을 아이템 유형별로 확인합니다.

| 아이템 | 초기값 | 기대값 |
|--------|--------|--------|
| 일반 아이템 | SellIn=5, Quality=0 | Quality=0 |
| 일반 아이템 (기한 초과) | SellIn=-1, Quality=0 | Quality=0 |
| Aged Brie | (Quality는 증가하므로 하한 도달 불가 — 생략) | — |
| Backstage passes (기한 초과) | SellIn=-1, Quality=0 | Quality=0 |

---

### `test_quality_maximum_is_50` — 상한 검증

Quality가 50인 상태에서 update해도 초과하지 않음을 아이템 유형별로 확인합니다.

| 아이템 | 초기값 | 기대값 |
|--------|--------|--------|
| 일반 아이템 | (Quality는 감소하므로 상한 도달 불가 — 생략) | — |
| Aged Brie | SellIn=5, Quality=50 | Quality=50 |
| Aged Brie (기한 초과) | SellIn=-1, Quality=50 | Quality=50 |
| Backstage passes (SellIn≤5) | SellIn=5, Quality=50 | Quality=50 |

---

## 구현 코드

```python
class TestQualityBounds(unittest.TestCase):

    def test_quality_minimum_is_0(self):
        cases = [
            Item("normal item", 5, 0),
            Item("normal item", -1, 0),
            Item("Backstage passes to a TAFKAL80ETC concert", -1, 0),
        ]
        for item in cases:
            with self.subTest(name=item.name, sell_in=item.sell_in):
                update(item)
                self.assertGreaterEqual(item.quality, 0)

    def test_quality_maximum_is_50(self):
        cases = [
            Item("Aged Brie", 5, 50),
            Item("Aged Brie", -1, 50),
            Item("Backstage passes to a TAFKAL80ETC concert", 5, 50),
        ]
        for item in cases:
            with self.subTest(name=item.name, sell_in=item.sell_in):
                update(item)
                self.assertLessEqual(item.quality, 50)
```

---

## `subTest` 사용 이유

여러 아이템을 루프로 검증할 때 `subTest`를 사용하면 하나가 실패해도 나머지 케이스를 계속 실행해서 어느 아이템에서 위반이 발생했는지 개별적으로 확인할 수 있습니다.

---

## 검증 포인트

- [ ] 일반 아이템: Quality가 0 미만이 되지 않는가
- [ ] 기한 초과 일반 아이템: Quality가 0 미만이 되지 않는가
- [ ] Aged Brie: Quality가 50을 초과하지 않는가
- [ ] Backstage passes: Quality가 50을 초과하지 않는가
