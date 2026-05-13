"""
D1_incubation_days.py — Distribution analysis of incubation_days
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from analysis_base import analyze_variable

if __name__ == "__main__":
    analyze_variable("hantavirus_clinical.csv", "incubation_days", "Incubation Days")
