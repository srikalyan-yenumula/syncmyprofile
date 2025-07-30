import os
from datetime import datetime

LOG_DIR = "secure_logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log_extracted_text(profile_text, filename="extracted_profile.txt"):
    log_path = os.path.join(LOG_DIR, filename)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n--- Extracted at {datetime.now()} ---\n")
        f.write(profile_text)

def log_ai_analysis(analysis_text, filename="ai_analysis.txt"):
    log_path = os.path.join(LOG_DIR, filename)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n--- AI Analysis at {datetime.now()} ---\n")
        f.write(analysis_text)
