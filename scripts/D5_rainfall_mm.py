"""
D5_rainfall_mm.py — Distribution analysis of rainfall_mm
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from analysis_base import analyze_variable

if __name__ == "__main__":
    analyze_variable("hantavirus_environmental.csv", "rainfall_mm", "Rainfall (mm)")
