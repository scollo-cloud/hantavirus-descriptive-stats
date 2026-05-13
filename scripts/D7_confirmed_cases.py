"""
D7_confirmed_cases.py — Distribution analysis of confirmed_cases
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from analysis_base import analyze_variable

if __name__ == "__main__":
    analyze_variable("hantavirus_country_yearly.csv", "confirmed_cases", "Confirmed Cases")
