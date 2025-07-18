# app.py
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
import json

from database import init_db, save_project, load_projects, get_project_filters
from llm_processor import process_query
from data_fetcher import fetch_calgary_data

app = Flask(__name__)
CORS(app)
init_db()

@app.route('/api/buildings', methods=['GET'])
def get_buildings():
    try:
        buildings = fetch_calgary_data()
        return jsonify(buildings)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch building data: {e}"}), 500

@app.route('/api/query', methods=['POST'])
def query_buildings():
    """
    1) Parse the NL query into criteria via process_query()
    2) Fetch ALL buildings via fetch_calgary_data()
    3) Filter them server‑side
    4) Return the filtered list of building objects
    """
    payload = request.json or {}
    query = payload.get('query', '').strip()
    if not query:
        return jsonify({"error": "Query is required"}), 400

    # 1) Get the filter criteria from the LLM
    criteria = process_query(query)
    if 'error' in criteria:
        return jsonify({"error": criteria['error'], "raw": criteria.get('raw')}), 400

    # 2) Load the full dataset
    try:
        buildings = fetch_calgary_data()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch building data: {e}"}), 500

    # 3) Apply the LLM's criteria
    def matches(b):
        attr = criteria.get('attribute')
        op   = criteria.get('operator')
        val  = criteria.get('value')
        bval = b.get(attr)
        if bval is None:
            return False
        try:
            if op == '>':   return bval >  val
            if op == '<':   return bval <  val
            if op == '>=':  return bval >= val
            if op == '<=':  return bval <= val
            if op == '==':
                # case-insensitive string match if needed
                if isinstance(bval, str):
                    return bval.lower() == str(val).lower()
                return bval == val
        except Exception:
            return False
        return False

    filtered = [b for b in buildings if matches(b)]

    # 4) Return the filtered buildings
    return jsonify(filtered), 200

# --- your other endpoints unchanged ---

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
