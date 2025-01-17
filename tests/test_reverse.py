import logging
import unittest

import jageocoder
from jageocoder.address import AddressLevel

logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)


class TestReverseMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        jageocoder.init(mode="r")

    def test_aza_level(self):
        """
        Test reverse lookup of an address from coordinates in general conditions.
        """
        results = jageocoder.reverse(x=139.428969, y=35.625779)
        candidate_names = [x['candidate']['fullname'] for x in results]

        self.assertEqual(len(candidate_names), 3)
        self.assertEqual(candidate_names[0], ["東京都", "多摩市", "落合", "一丁目"])
        self.assertEqual(candidate_names[1], ["東京都", "多摩市", "愛宕", "四丁目"])
        self.assertEqual(candidate_names[2], ["東京都", "多摩市", "豊ケ丘", "一丁目"])

    def test_block_level(self):
        """
        Test reverse lookup of an address from coordinates in general conditions
        at Block level.
        """
        results = jageocoder.reverse(
            x=139.428969, y=35.625779, level=AddressLevel.BLOCK)
        candidate_names = [x['candidate']['fullname'] for x in results]

        self.assertEqual(len(candidate_names), 3)
        self.assertTrue(
            ["東京都", "多摩市", "落合", "一丁目", "15番地"] in candidate_names
        )

    def test_edge_case(self):
        """
        Test for the case where the specified coordinates are at the edge of
        the land and cannot form a Delaunay triangle.
        """
        results = jageocoder.reverse(
            y=35.720882, x=140.869360, level=AddressLevel.AZA)
        candidate_names = [x['candidate']['fullname'] for x in results]
        self.assertTrue(len(candidate_names) >= 2)
        self.assertEqual(
            ["千葉県", "銚子市", "海鹿島町"], candidate_names[0]
        )
        self.assertEqual(
            ["千葉県", "銚子市", "君ケ浜"], candidate_names[1]
        )

    def test_edge_block_level(self):
        """
        Test for the case where the specified coordinates are at the edge of
        the land and cannot form a Delaunay triangle and lookup at Block level.
        """
        results = jageocoder.reverse(
            y=35.720882, x=140.869360, level=AddressLevel.BLOCK)
        candidate_names = [x['candidate']['fullname'] for x in results]
        self.assertTrue(len(candidate_names) >= 2)
        self.assertTrue(
            ["千葉県", "銚子市", "海鹿島町", "5245番地"] in candidate_names
        )
        self.assertTrue(
            ["千葉県", "銚子市", "海鹿島町", "5244番地"] in candidate_names
        )

    def test_island(self):
        """
        Test for the case where there are not a sufficient number of
        address nodes around, such as on an island.
        """
        results = jageocoder.reverse(x=142.155764, y=26.660128)
        candidate_names = [x['candidate']['fullname'] for x in results]
        self.assertTrue(len(candidate_names) >= 1)
        self.assertTrue(
            ["東京都", "小笠原村", "母島"] in candidate_names
        )

    def test_hachijo(self):
        """
        Test for the case where there are not a sufficient number of
        address nodes around, such as on an island.
        """
        results = jageocoder.reverse(
            x=139.79204562036716, y=33.113018869587904)
        candidate_names = [x['candidate']['fullname'] for x in results]
        self.assertTrue(len(candidate_names) >= 1)
        self.assertIn(
            candidate_names[0], (
                ["東京都", "八丈町", "宮ノ平"],
                ["東京都", "八丈町", "中道"]),
        )
