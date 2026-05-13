"""
D8_cfr.py — Distribution analysis of case_fatality_rate
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from analysis_base import analyze_variable

if __name__ == "__main__":
    analyze_variable("hantavirus_country_yearly.csv", "case_fatality_rate", "Case Fatality Rate")
