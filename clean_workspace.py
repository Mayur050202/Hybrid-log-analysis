import os

def tidy_project():
    print("=== STARTING WORKSPACE MANAGEMENT SWEEP ===")
    
    # Files to keep inside core source control
    files_to_preserve = [
        "initialize.py", 
        "stage2_chaos_engine.py", 
        "stage3_report_dashboard.py", 
        "evaluate_metrics.py"
    ]
    
    # Unused structural variants from mid-development phase
    deprecated_files = ["download_data.py", "verify_stage1.py", "stage2_ml_engine.py"]
    
    removed_count = 0
    for file in deprecated_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"[✓] Purged intermediate file: {file}")
            removed_count += 1
            
    print(f"\n[!] Clean task finished. {removed_count} redundant script files safely removed.")
    print("[!] Active operational framework preserved: initialize, chaos_engine, metrics, dashboard.")
    print("=== WORKSPACE COMMITTED AS PRISTINE ===")

if __name__ == "__main__":
    tidy_project()
