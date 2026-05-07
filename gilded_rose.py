from abc import ABC, abstractmethod

AGED_BRIE = "Aged Brie"
SULFURAS = "Sulfuras, Hand of Ragnaros"
BACKSTAGE_PASSES = "Backstage passes to a TAFKAL80ETC concert"


class ItemUpdater(ABC):
    _registry: dict = {}

    def __init_subclass__(cls, item_name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if item_name:
            ItemUpdater._registry[item_name] = cls()

    @classmethod
    def for_item(cls, item):
        return cls._registry.get(item.name, NormalItemUpdater())

    @abstractmethod
    def update(self, item):
        pass

    def _clamp_quality(self, item):
        item.quality = max(0, min(50, item.quality))


class NormalItemUpdater(ItemUpdater):
    def update(self, item):
        item.sell_in -= 1
        item.quality -= 1
        if item.sell_in < 0:
            item.quality -= 1
        self._clamp_quality(item)


class AgedBrieUpdater(ItemUpdater, item_name=AGED_BRIE):
    def update(self, item):
        item.sell_in -= 1
        item.quality += 1
        if item.sell_in < 0:
            item.quality += 1
        self._clamp_quality(item)


class SulfurasUpdater(ItemUpdater, item_name=SULFURAS):
    def update(self, item):
        pass


class BackstagePassesUpdater(ItemUpdater, item_name=BACKSTAGE_PASSES):
    def update(self, item):
        item.sell_in -= 1
        if item.sell_in < 0:
            item.quality = 0
            return
        item.quality += 1
        if item.sell_in < 10:
            item.quality += 1
        if item.sell_in < 5:
            item.quality += 1
        self._clamp_quality(item)


class GildedRose(object):
    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            ItemUpdater.for_item(item).update(item)


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
