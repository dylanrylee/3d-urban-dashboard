# llm_processor.py (updated parsing)

# Load environment variables from a .env file
from dotenv import load_dotenv
load_dotenv()

import os
import requests
import json
import google.generativeai as genai

# Retrieve the Gemini API key from environment and configure the client
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# Use the Gemini Flash model for lightweight, fast responses
PRIMARY_MODEL = "gemini-1.5-flash"

def _call_hf(model, prompt):
    """
    Call the specified LLM model with a prompt and return its raw text output.
    """
    # Generate content via the Google Generative AI client
    resp = genai.GenerativeModel(model).generate_content(prompt)
    text = resp.text
    # Log the raw output for debugging
    print(f"[LLM:{model}] raw output:\n{text}")
    return text

def process_query(query):
    """
    Convert a free‑text user query into structured filtering criteria.
    Returns a dict with keys: attribute, operator, and value, or an error.
    """
    # Ensure the API key is set
    if not API_KEY:
        return {"error": "Missing GEMINI_API_KEY"}

    # Build the prompt instructing the model to output only a JSON object
    prompt = (
        "Output ONLY a JSON object with keys:\n"
        "  attribute: one of height, zoning, value, etc.\n"
        "  operator: >, <, >=, <=, or ==\n"
        "  value: a number or string\n"
        f"For this query: \"{query}\""
    )

    # Call the LLM and get its raw response
    text = _call_hf(PRIMARY_MODEL, prompt)

    # STEP 1: Strip fenced code blocks (```json ... ```)
    body = text.strip()
    if body.startswith("```"):
        # Remove leading backticks and optional 'json' marker
        body = body.lstrip("`")                 # drop backticks
        body = body.replace("json", "", 1).lstrip()  # drop optional 'json'
        # Remove trailing backticks if present
        if body.endswith("```"):
            body = body[:-3].strip()

    # STEP 2: Parse the cleaned text as JSON
    try:
        criteria = json.loads(body)
        return criteria
    except Exception as e:
        # Log parsing errors and return an error payload including raw body
        print("[LLM] JSON parse error:", e, "\n--body was--\n", repr(body))
        return {"error": "Failed to parse LLM response", "raw": body}
