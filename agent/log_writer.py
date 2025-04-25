import csv
import os
from datetime import datetime

LOG_FILE = "logs.csv"

def log_result(query: str, success: bool, confidence: float, fallback_reason: str = None):
    log_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        if not log_exists:
            writer.writerow(["timestamp", "query", "result", "confidence", "fallback_reason"])
        
        writer.writerow([
            datetime.utcnow().isoformat(),
            query,
            "Success" if success else "Fallback",
            confidence,
            fallback_reason if fallback_reason else "N/A"
        ])