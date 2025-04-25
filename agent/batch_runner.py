import os
import csv
from datetime import datetime
from cli import agent_main

queries = [
    "What does error code 137 mean in Docker?",
    "Explain how AWS S3 versioning works.",
    "How do you create a virtual environment in Python?",
    "What is a 502 Bad Gateway error?",
    "Best practices for handling API rate limits?",
    "What is Zero Trust architecture?",
    "Explain OAuth2 authorization flow.",
    "Common causes of high memory usage in Kubernetes?",
    "How does serverless architecture scale?",
    "What is optimistic concurrency control in databases?"
]

BATCH_LOG_FILE = "batch_logs.csv"

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