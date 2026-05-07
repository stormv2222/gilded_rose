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