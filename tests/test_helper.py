import unittest
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

# Add project root and scripts directory to sys.path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / "scripts"))
from scripts.helper import (
    iqr_outliers, 
    kurtosis_description, 
    recommend_center, 
    recommend_spread
)

class TestHelper(unittest.TestCase):

    def test_iqr_outliers(self):
        # Create a series with known outliers
        data = pd.Series([10, 11, 12, 13, 14, 15, 100])
        outliers = iqr_outliers(data)
        self.assertEqual(len(outliers), 1)
        self.assertEqual(outliers.iloc[0], 100)

    def test_kurtosis_description(self):
        self.assertEqual(kurtosis_description(-1), "lighter tails + flatter peak than normal")
        self.assertEqual(kurtosis_description(1), "heavier tails + sharper peak than normal")
        self.assertEqual(kurtosis_description(0), "similar to normal (mesokurtic)")

    def test_recommend_center_symmetric(self):
        # Symmetric data
        data = pd.Series([1, 2, 3, 4, 5])
        self.assertEqual(recommend_center(data), "mean")

    def test_recommend_center_skewed(self):
        # Heavily skewed data
        data = pd.Series([1, 2, 3, 4, 100])
        self.assertTrue("median" in recommend_center(data))

    def test_recommend_spread_symmetric(self):
        # Symmetric data
        data = pd.Series([1, 2, 3, 4, 5])
        self.assertEqual(recommend_spread(data), "standard deviation")

    def test_recommend_spread_skewed(self):
        # Heavily skewed data
        data = pd.Series([1, 2, 3, 4, 100])
        self.assertTrue("IQR" in recommend_spread(data))

if __name__ == "__main__":
    unittest.main()
