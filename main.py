"""
main.py — Master execution script for the Hantavirus analysis project.
This script runs the entire pipeline from data loading to report generation.
"""
import subprocess
import sys
from pathlib import Path

# List of scripts to run in order
PIPELINE = [
    "scripts/01_load_explore.py",
    "scripts/02_summary_stats.py",
    "scripts/D1_incubation_days.py",
    "scripts/D2_hospital_days.py",
    "scripts/D2b_hospital_investigation.py",
    "scripts/D3_icu_days.py",
    "scripts/D3b_icu_investigation.py",
    "scripts/D4_avg_temp_c.py",
    "scripts/D5_rainfall_mm.py",
    "scripts/D6_rodent_abundance.py",
    "scripts/D7_confirmed_cases.py",
    "scripts/D8_cfr.py",
    "scripts/C_outlier_investigation.py",
    "scripts/E1_comparative_violins.py",
    "scripts/E2_bar_chart_critique.py",
    "scripts/F_summary_tables.py",
    "scripts/dashboard.py",
]

def run_script(script_path: str):
    print(f"\n>>> Running {script_path}...")
    try:
        result = subprocess.run([sys.executable, script_path], capture_output=False, check=True)
        print(f"✅ Finished {script_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_path}: {e}")
        return False

def main():
    print("🚀 Starting Hantavirus Analysis Pipeline")
    
    # Ensure we are in the project root
    project_root = Path(__file__).parent
    
    results = []
    for script in PIPELINE:
        script_path = project_root / script
        if not script_path.exists():
            print(f"⚠ Skipping missing script: {script}")
            results.append((script, "MISSING"))
            continue
        
        success = run_script(str(script_path))
        results.append((script, "SUCCESS" if success else "FAILED"))
    
    print("\n" + "="*40)
    print("📋 PIPELINE SUMMARY")
    print("="*40)
    for script, status in results:
        icon = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "⚠"
        print(f"{icon} {script:35s} {status}")
    print("="*40)

    if any(status == "FAILED" for _, status in results):
        print("\n✨ Pipeline complete with some errors. See summary above.")
    else:
        print("\n✨ Pipeline complete! All figures and the dashboard have been updated.")
    
    print("To compile the reports, navigate to the 'report/' directory and run 'pdflatex detailed_report.tex'")

if __name__ == "__main__":
    main()
