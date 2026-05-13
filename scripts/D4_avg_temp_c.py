"""
D4_avg_temp_c.py — Distribution analysis of avg_temp_c
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from analysis_base import analyze_variable

if __name__ == "__main__":
    analyze_variable("hantavirus_environmental.csv", "avg_temp_c", "Average Temperature (°C)")
