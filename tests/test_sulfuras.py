import unittest
from gilded_rose import GildedRose, Item


def update(item):
    GildedRose([item]).update_quality()
    return item


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


if __name__ == "__main__":
    unittest.main()
