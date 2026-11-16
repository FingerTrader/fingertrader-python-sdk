from __future__ import annotations

import unittest

from finger_trader import SMA, crosses_above, crosses_below, sma


class ChartAlignmentTests(unittest.TestCase):
    def test_sma_and_crossings_share_chart_warmup_and_equality(self) -> None:
        prices = [10, 10, 10, 10, 13, 13, 7, 7]
        fast, slow = sma(prices, 2), sma(prices, 3)
        self.assertEqual(fast, [None, 10, 10, 10, 11.5, 13, 10, 7])
        self.assertEqual(slow, [None, None, 10, 10, 11, 12, 11, 9])
        above = [i for i in range(1, len(prices))
                 if crosses_above(fast[i-1], slow[i-1], fast[i], slow[i])]
        below = [i for i in range(1, len(prices))
                 if crosses_below(fast[i-1], slow[i-1], fast[i], slow[i])]
        self.assertEqual(above, [4])
        self.assertEqual(below, [6])

    def test_stream_reset_retains_no_other_run_history(self) -> None:
        indicator = SMA(3)
        for price in [1, 3, 7, 2, 9]:
            indicator.update(price)
        indicator.reset()
        self.assertEqual([indicator.update(v) for v in [5, 5, 5]], [None, None, 5])

    def test_missing_and_nonfinite_values_never_create_orders(self) -> None:
        for value in [None, float('nan'), float('inf'), -float('inf')]:
            self.assertFalse(crosses_above(value, 2, 3, 2))
            self.assertFalse(crosses_below(3, 2, value, 2))
