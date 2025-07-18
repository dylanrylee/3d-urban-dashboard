# llm_processor.py (updated parsing)
from dotenv import load_dotenv
load_dotenv()

import os, requests, json
import google.generativeai as genai

API_KEY    = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

PRIMARY_MODEL  = "gemini-1.5-flash"

def _call_hf(model, prompt):
    resp = genai.GenerativeModel(model).generate_content(prompt)
    text = resp.text
    print(f"[LLM:{model}] raw output:\n{text}")
    return text

def process_query(query):
    if not API_KEY:
        return {"error": "Missing GEMINI_API_KEY"}

    prompt = (
      "Output ONLY a JSON object with keys:\n"
      "  attribute: one of height, zoning, value, etc.\n"
      "  operator: >, <, >=, <=, or ==\n"
      "  value: a number or string\n"
      f"For this query: \"{query}\""
    )

    text = _call_hf(PRIMARY_MODEL, prompt)

    # 1) Strip fenced code blocks:
    #    Remove ```json\n at the start and trailing ``` if present
    body = text.strip()
    if body.startswith("```"):
        # remove leading ```json or ```
        body = body.lstrip("`")                          # drop backticks
        body = body.replace("json", "", 1).lstrip()      # drop optional 'json'
        # remove trailing backticks
        if body.endswith("```"):
            body = body[:-3].strip()

    # 2) Now parse JSON
    try:
        criteria = json.loads(body)
        return criteria
    except Exception as e:
        print("[LLM] JSON parse error:", e, "\n--body was--\n", repr(body))
        return {"error": "Failed to parse LLM response", "raw": body}
