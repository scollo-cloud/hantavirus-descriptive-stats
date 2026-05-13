"""
D2_hospital_days.py — Distribution analysis of hospital_days
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from analysis_base import analyze_variable

if __name__ == "__main__":
    analyze_variable("hantavirus_clinical.csv", "hospital_days", "Hospital Days")
