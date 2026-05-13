"""
D6_rodent_abundance.py — Distribution analysis of rodent_abundance_index
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from analysis_base import analyze_variable

if __name__ == "__main__":
    analyze_variable("hantavirus_environmental.csv", "rodent_abundance_index", "Rodent Abundance Index")
