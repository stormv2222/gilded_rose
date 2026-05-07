import unittest
from gilded_rose import GildedRose, Item


def update(item):
    GildedRose([item]).update_quality()
    return item


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


if __name__ == "__main__":
    unittest.main()
