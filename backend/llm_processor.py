import requests
import json
from os import environ

HUGGINGFACE_API_KEY = environ.get('HUGGINGFACE_API_KEY')

def process_query(query):
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {
        "inputs": f"Extract the filter from this query: '{query}'. Return a JSON object with 'attribute' (e.g., height), 'operator' (e.g., >), and 'value' (e.g., 100).",
        "parameters": {"max_new_tokens": 100}
    }
    response = requests.post(
        "https://api-inference.huggingface.co/models/mixtral-8x7b-instruct-v0.1",
        headers=headers,
        json=payload
    )
    if response.status_code == 200:
        result = response.json()[0]['generated_text']
        try:
            return json.loads(result.split('```json\n')[1].split('\n```')[0])
        except:
            return {"error": "Failed to parse LLM response"}
    return {"error": "LLM API request failed"}