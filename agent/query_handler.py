import os
import json
import argparse
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from openai import OpenAI

# Load environment variables
load_dotenv()

# Setup OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Define your expected schema ---
class AnswerSchema(BaseModel):
    answer: str
    confidence: float

# --- Fallback Answer ---
fallback_answer = {
    "answer": "I'm sorry, I cannot answer this question right now. Please check the official documentation.",
    "confidence": 0.5
}

# --- Query the LLM ---
def get_llm_response(query: str) -> dict:
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4-turbo"),
            messages=[
                {"role": "system", "content": "Respond in JSON format: {\"answer\": string, \"confidence\": float}"},
                {"role": "user", "content": query}
            ],
            temperature=0
        )
        raw_content = response.choices[0].message.content
        return json.loads(raw_content)
    except (json.JSONDecodeError, Exception) as e:
        return None

# --- Validate the LLM output ---
def validate_output(output: dict) -> bool:
    try:
        AnswerSchema.parse_obj(output)
        return True
    except ValidationError:
        return False

# --- Main Agent Logic ---
def agent_main(user_query: str):
    output = get_llm_response(user_query)

    if output and validate_output(output):
        return output, False  # Success, no fallback
    else:
        return fallback_answer, True  # Fallback triggered

# --- CLI Interface ---
def cli():
    parser = argparse.ArgumentParser(description="Structured CLI LLM Agent")
    parser.add_argument("--query", type=str, required=True, help="User query")
    args = parser.parse_args()

    final_answer, fallback_used = agent_main(args.query)

    print("\n--- Agent Response ---")
    print(json.dumps(final_answer, indent=2))
    if fallback_used:
        print("(Fallback triggered)")

if __name__ == "__main__":
    cli()