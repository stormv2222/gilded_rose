# 가독성 향상 리팩토링 계획

---

## 1. 현재 코드의 문제점

### 문제 1 — 최대 5단계 중첩 조건문

```python
if item.sell_in < 0:
    if item.name != "Aged Brie":
        if item.name != "Backstage passes to a TAFKAL80ETC concert":
            if item.quality > 0:
                if item.name != "Sulfuras, Hand of Ragnaros":
                    item.quality = item.quality - 1
```

로직의 흐름을 파악하려면 조건문을 역추적해야 하며, 어떤 아이템이 어떤 규칙을 따르는지 한눈에 파악할 수 없습니다.

---

### 문제 2 — 문자열 직접 비교로 아이템 분기

```python
if item.name != "Aged Brie" and item.name != "Backstage passes to a TAFKAL80ETC concert":
```

아이템 이름이 코드 전역에 하드코딩되어 있어, 이름이 바뀌면 여러 곳을 수정해야 합니다.

---

### 문제 3 — 아이템별 규칙이 하나의 메서드에 혼재

`update_quality` 하나에 일반 아이템, Aged Brie, Backstage passes, Sulfuras의 규칙이 모두 뒤섞여 있어 특정 아이템의 규칙만 파악하기 어렵습니다.

---

### 문제 4 — 의도가 불명확한 표현

```python
item.quality = item.quality - item.quality  # 0으로 초기화 의도
item.quality = item.quality - 1             # -= 1 로 축약 가능
item.quality = item.quality + 1             # += 1 로 축약 가능
```

---

## 2. 리팩토링 목표

SPEC의 규칙 구조(아이템별 독립 규칙)가 코드 구조에 그대로 드러나도록 합니다.
동작은 변경하지 않으며, 가독성만 개선합니다.

---

## 3. 리팩토링 항목

### Step 1 — 아이템 이름 상수화

아이템 이름을 클래스 상수로 추출하여 문자열 하드코딩을 제거합니다.

```python
# Before
if item.name == "Aged Brie":

# After
AGED_BRIE = "Aged Brie"
SULFURAS = "Sulfuras, Hand of Ragnaros"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"

if item.name == AGED_BRIE:
```

---

### Step 2 — 아이템 유형 판별 메서드 추출

아이템 이름 비교를 메서드로 감싸 의미를 명확히 합니다.

```python
def _is_aged_brie(self, item):
    return item.name == AGED_BRIE

def _is_sulfuras(self, item):
    return item.name == SULFURAS

def _is_backstage_passes(self, item):
    return item.name == BACKSTAGE_PASSES
```

---

### Step 3 — 아이템별 업데이트 메서드 분리

각 아이템 유형의 규칙을 독립 메서드로 추출합니다.
`update_quality`는 분기만 담당하고, 규칙 자체는 각 메서드에 위임합니다.

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

def _update_normal_item(self, item): ...
def _update_aged_brie(self, item): ...
def _update_backstage_passes(self, item): ...
```

---

### Step 4 — Quality 경계값 보정 메서드 추출

Quality의 0 하한 / 50 상한 보정 로직을 메서드로 추출하여 각 업데이트 메서드에서 재사용합니다.

```python
def _clamp_quality(self, item):
    item.quality = max(0, min(50, item.quality))
```

---

### Step 5 — 연산자 및 표현 정리

| Before | After |
|--------|-------|
| `item.quality = item.quality - 1` | `item.quality -= 1` |
| `item.quality = item.quality + 1` | `item.quality += 1` |
| `item.quality = item.quality - item.quality` | `item.quality = 0` |

---

## 4. 리팩토링 후 구조

```
GildedRose
├── update_quality()              # 아이템 순회 및 유형별 분기
├── _is_aged_brie(item)
├── _is_sulfuras(item)
├── _is_backstage_passes(item)
├── _update_normal_item(item)     # 일반 아이템 규칙
├── _update_aged_brie(item)       # Aged Brie 규칙
├── _update_backstage_passes(item)# Backstage passes 규칙
└── _clamp_quality(item)          # Quality 경계값 보정
```

---

## 5. 리팩토링 진행 순서

| 순서 | 항목 | 비고 |
|------|------|------|
| 1 | 상수 추출 (Step 1) | 가장 작은 변경, 동작 영향 없음 |
| 2 | 판별 메서드 추출 (Step 2) | 상수 기반, 테스트로 검증 가능 |
| 3 | 업데이트 메서드 분리 (Step 3) | 핵심 리팩토링, 기존 테스트로 회귀 검증 |
| 4 | 경계값 보정 추출 (Step 4) | Step 3 이후 중복 제거 |
| 5 | 표현 정리 (Step 5) | 마지막 마무리 |

---

## 6. 회귀 검증

각 Step 완료 후 기존 unittest를 실행하여 동작 변경이 없음을 확인합니다.

```
pytest tests/ -v
```

---

## 7. Phase별 상세 진행 계획

### Phase 1 — 아이템 이름 상수화

**변경 범위**: `gilded_rose.py` 상단에 상수 3개 추가, 문자열 리터럴 전체 교체

**변경 전**
```python
class GildedRose(object):
    def update_quality(self):
        for item in self.items:
            if item.name != "Aged Brie" and item.name != "Backstage passes to a TAFKAL80ETC concert":
                if item.quality > 0:
                    if item.name != "Sulfuras, Hand of Ragnaros":
                        ...
```

**변경 후**
```python
AGED_BRIE = "Aged Brie"
SULFURAS = "Sulfuras, Hand of Ragnaros"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"

class GildedRose(object):
    def update_quality(self):
        for item in self.items:
            if item.name != AGED_BRIE and item.name != BACKSTAGE_PASSES:
                if item.quality > 0:
                    if item.name != SULFURAS:
                        ...
```

**검증**: `pytest tests/ -v` — 동작 변경 없으므로 전체 통과 확인

---

### Phase 2 — 아이템 유형 판별 메서드 추출

**변경 범위**: `GildedRose` 클래스에 판별 메서드 3개 추가, `update_quality` 내 비교식 교체

**변경 전**
```python
if item.name != AGED_BRIE and item.name != BACKSTAGE_PASSES:
    ...
if item.name != SULFURAS:
    item.sell_in = item.sell_in - 1
```

**변경 후**
```python
def _is_aged_brie(self, item):
    return item.name == AGED_BRIE

def _is_sulfuras(self, item):
    return item.name == SULFURAS

def _is_backstage_passes(self, item):
    return item.name == BACKSTAGE_PASSES

# update_quality 내부
if not self._is_aged_brie(item) and not self._is_backstage_passes(item):
    ...
if not self._is_sulfuras(item):
    item.sell_in = item.sell_in - 1
```

**검증**: `pytest tests/ -v` — 전체 통과 확인

---

### Phase 3 — 아이템별 업데이트 메서드 분리

**변경 범위**: `update_quality`의 규칙 로직을 아이템별 메서드로 추출, `update_quality`는 분기만 담당

**변경 전**
```python
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

**검증**: `pytest tests/ -v` — 전체 통과 확인 (핵심 단계, 회귀 여부 집중 확인)

---

### Phase 4 — Quality 경계값 보정 메서드 추출

**변경 범위**: `_clamp_quality` 메서드 추가, 각 업데이트 메서드의 인라인 경계 처리 교체

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
def _clamp_quality(self, item):
    item.quality = max(0, min(50, item.quality))

def _update_aged_brie(self, item):
    item.sell_in = item.sell_in - 1
    item.quality = item.quality + 1
    if item.sell_in < 0:
        item.quality = item.quality + 1
    self._clamp_quality(item)
```

**검증**: `pytest tests/ -v` — 전체 통과 확인

---

### Phase 5 — 연산자 및 표현 정리

**변경 범위**: 각 업데이트 메서드 내 연산식 표현 통일

**변경 내용**

| 위치 | Before | After |
|------|--------|-------|
| `_update_normal_item` | `item.quality = item.quality - 1` | `item.quality -= 1` |
| `_update_aged_brie` | `item.quality = item.quality + 1` | `item.quality += 1` |
| `_update_backstage_passes` | `item.quality = item.quality + 1` | `item.quality += 1` |
| `_update_normal_item` | `item.sell_in = item.sell_in - 1` | `item.sell_in -= 1` |
| `_update_aged_brie` | `item.sell_in = item.sell_in - 1` | `item.sell_in -= 1` |
| `_update_backstage_passes` | `item.sell_in = item.sell_in - 1` | `item.sell_in -= 1` |

**검증**: `pytest tests/ -v` — 전체 통과 확인
