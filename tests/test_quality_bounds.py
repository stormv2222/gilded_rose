import unittest
from gilded_rose import GildedRose, Item


def update(item):
    GildedRose([item]).update_quality()
    return item


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


if __name__ == "__main__":
    unittest.main()
