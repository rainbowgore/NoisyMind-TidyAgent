import os
import json
import time
import argparse
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from openai import OpenAI
from log_writer import log_result

# Load environment variables
load_dotenv()

# Setup OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Configurations ---
MAX_RETRIES = 2
CONFIDENCE_THRESHOLD = 0.7
RETRY_BACKOFF_SECONDS = 2

# --- Define expected schema ---
class AnswerSchema(BaseModel):
    answer: str
    confidence: float

# --- Fallback Answer ---
fallback_answer = {
    "answer": "I'm sorry, I cannot answer this question right now. Please check the official documentation.",
    "confidence": 0.5
}

# --- Metrics ---
metrics = {
    "success": 0,
    "fallback_total": 0,
    "fallback_api_error": 0,
    "fallback_json_error": 0,
    "fallback_confidence_low": 0
}

# --- Query the LLM with retries ---
def get_llm_response(query: str) -> (dict, str):
    attempt = 0
    while attempt <= MAX_RETRIES:
        try:
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4-turbo"),
                messages=[
                    {"role": "system", "content": """You must only respond in strict JSON format:
{"answer": string, "confidence": float}

Rules:
- Do not add any explanation or commentary outside the JSON object.
- Do not use markdown formatting (no ```json blocks).
- Always fill both fields exactly once.
- If unsure or unable to answer reliably, respond with:
  {"answer": "Cannot answer reliably.", "confidence": 0.0}
- Use null or 0.0 explicitly if needed. Never omit fields.
- No apologies, disclaimers, or notes.
- No extra fields beyond "answer" and "confidence".
- Output must be valid JSON parseable by Python's json.loads().
""" },
                    {"role": "user", "content": f"Remember: JSON only. No extra text. Query: {query}"}
                ],
                temperature=0
            )
            raw_content = response.choices[0].message.content
            
            # Auto-strip ```json wrapping if exists
            if raw_content.startswith("```json"):
                raw_content = raw_content.replace("```json", "").replace("```", "").strip()

            return json.loads(raw_content), None  # Successful parse
        except Exception as e:
            print(f"API Error on attempt {attempt + 1}: {e}")
            if attempt == MAX_RETRIES:
                return None, "api_error"
            time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
            attempt += 1

# --- Validate LLM output ---
def validate_output(output: dict) -> bool:
    try:
        AnswerSchema.model_validate(output)
        return True
    except ValidationError:
        return False

# --- Main Agent Logic ---
def agent_main(user_query: str):
    output, error_type = get_llm_response(user_query)

    if output is None:
        metrics["fallback_total"] += 1
        metrics["fallback_api_error"] += 1
        fallback_used = True
        final_output = fallback_answer
    elif not validate_output(output):
        metrics["fallback_total"] += 1
        metrics["fallback_json_error"] += 1
        fallback_used = True
        final_output = fallback_answer
    elif output.get("confidence", 0.0) < CONFIDENCE_THRESHOLD:
        metrics["fallback_total"] += 1
        metrics["fallback_confidence_low"] += 1
        fallback_used = True
        final_output = fallback_answer
    else:
        metrics["success"] += 1
        fallback_used = False
        final_output = output

    return final_output, fallback_used  # ✅ EXACT TWO VALUES

# --- CLI Interface ---
def cli():
    parser = argparse.ArgumentParser(description="Structured CLI LLM Agent with Reliability Upgrades")
    parser.add_argument("--query", type=str, required=True, help="User query")
    args = parser.parse_args()

    final_answer, fallback_used, fallback_reason = agent_main(args.query)

    print("\n--- Agent Response ---")
    print(json.dumps(final_answer, indent=2))
    if fallback_used:
        print(f"(Fallback triggered: {fallback_reason})")

    log_result(
        query=args.query,
        success=not fallback_used,
        confidence=final_answer.get("confidence", 0.0),
        fallback_reason=fallback_reason
    )

# --- Metrics Exporter ---
def export_metrics():
    with open("metrics.txt", "w") as f:
        f.write("# HELP agent_success_total Number of successful agent queries\n")
        f.write("# HELP agent_fallback_total Number of fallback agent queries\n")
        f.write("# HELP agent_fallback_api_error_total Number of API error fallbacks\n")
        f.write("# HELP agent_fallback_json_error_total Number of JSON parsing fallbacks\n")
        f.write("# HELP agent_fallback_confidence_low_total Number of low-confidence fallbacks\n\n")
        f.write(f"agent_success_total {metrics['success']}\n")
        f.write(f"agent_fallback_total {metrics['fallback_total']}\n")
        f.write(f"agent_fallback_api_error_total {metrics['fallback_api_error']}\n")
        f.write(f"agent_fallback_json_error_total {metrics['fallback_json_error']}\n")
        f.write(f"agent_fallback_confidence_low_total {metrics['fallback_confidence_low']}\n")

if __name__ == "__main__":
    cli()
    export_metrics()