import os
import csv
from datetime import datetime
from cli import agent_main

BATCH_LOG_FILE = "batch_logs.csv"

def load_queries():
    queries = []
    with open("queries.txt", "r") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                queries.append(line)
    return queries

def init_log():
    with open(BATCH_LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "query", "result", "confidence"])

def log_batch_result(query: str, success: bool, confidence: float):
    with open(BATCH_LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.utcnow().isoformat(),
            query,
            "Success" if success else "Fallback",
            confidence
        ])

def run_batch():
    print("\nRunning batch evaluation...\n")
    queries = load_queries()
    init_log()

    success_count = 0
    fallback_count = 0
    confidence_scores = []

    for query in queries:
        result, fallback_used = agent_main(query)
        success = not fallback_used
        confidence = result.get("confidence", 0.0)

        log_batch_result(query, success, confidence)

        if success:
            success_count += 1
        else:
            fallback_count += 1

        confidence_scores.append(confidence)

        print(f"Query: {query}")
        print(f"Result: {'Success' if success else 'Fallback'} | Confidence: {confidence}")
        print("-" * 50)

    total = success_count + fallback_count
    avg_confidence = sum(confidence_scores) / total if total > 0 else 0

    print("\n=== Batch Evaluation Summary ===")
    print(f"Total Queries: {total}")
    print(f"Successes: {success_count} ({(success_count/total)*100:.2f}%)")
    print(f"Fallbacks: {fallback_count} ({(fallback_count/total)*100:.2f}%)")
    print(f"Average Confidence: {avg_confidence:.2f}")

if __name__ == "__main__":
    run_batch()