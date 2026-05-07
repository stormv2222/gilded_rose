import unittest
from gilded_rose import GildedRose, Item


def update(item):
    GildedRose([item]).update_quality()
    return item


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


if __name__ == "__main__":
    unittest.main()
