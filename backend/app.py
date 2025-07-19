from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env

from flask import Flask, request, jsonify
from flask_cors import CORS
import json

# Import database functions for project persistence
from database import (
    init_db,
    save_project,
    load_projects,        # returns list of {id, name, filters}
    get_project_filters,  # returns raw filters array for a project
    delete_project
)
# Import data-fetching and LLM-processing modules
from data_fetcher import fetch_calgary_data
from llm_processor import process_query

# Create Flask app and enable CORS for cross-origin requests
app = Flask(__name__)
CORS(app)

# Initialize SQLite database (creates projects table if missing)
init_db()

@app.route('/api/buildings', methods=['GET'])
def get_buildings():
    """
    GET /api/buildings
    Fetch raw building data (list of dicts) from the external API.
    Returns JSON list on success, or error message with 500 status.
    """
    try:
        buildings = fetch_calgary_data()
        return jsonify(buildings)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/api/query', methods=['POST'])
def query_buildings():
    """
    POST /api/query
    Body: { "query": "<NL query string>" }
    - Validate query payload
    - Use LLM to parse into filter criteria
    - Fetch fresh building data and apply filter logic
    - Return filtered list or error
    """
    payload = request.json or {}
    q = payload.get('query', '').strip()
    if not q:
        return jsonify(error="Query is required"), 400

    # Convert natural-language query to structured criteria
    criteria = process_query(q)
    if 'error' in criteria:
        # LLM parsing error
        return jsonify(error=criteria['error'], raw=criteria.get('raw')), 400

    try:
        buildings = fetch_calgary_data()
    except Exception as e:
        return jsonify(error=str(e)), 500

    # Define match function based on attribute/operator/value
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
                # Case-insensitive comparison for strings
                if isinstance(bval, str):
                    return bval.lower() == str(val).lower()
                return bval == val
        except:
            # Any comparison error yields no match
            return False

        return False

    # Return only buildings that match the criteria
    filtered = [b for b in buildings if matches(b)]
    return jsonify(filtered), 200

@app.route('/api/projects', methods=['POST'])
def save_project_endpoint():
    """
    POST /api/projects
    Body: { "username": "...", "projectName": "...", "filters": [<ids>] }
    - Validate inputs and save the filter list under the given user/name
    """
    data = request.json or {}
    user = data.get('username', '').strip()
    name = data.get('projectName', '').strip()
    filters = data.get('filters')

    # Validate required fields
    if not user or not name:
        return jsonify(error="username and projectName are required"), 400
    if not isinstance(filters, list):
        return jsonify(error="filters must be a list"), 400

    # Persist project
    save_project(user, name, json.dumps(filters))
    return jsonify(message="Project saved"), 200

@app.route('/api/projects/<username>', methods=['GET'])
def load_projects_endpoint(username):
    """
    GET /api/projects/<username>
    Return all saved projects (id, name, filters) for a user.
    """
    try:
        projects = load_projects(username)
        return jsonify(projects), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/api/project/<int:project_id>', methods=['GET'])
def load_project_filters(project_id):
    """
    GET /api/project/<id>
    Return the filters array for a specific project.
    """
    try:
        filt = get_project_filters(project_id)
        if filt is None:
            return jsonify(error="Project not found"), 404
        return jsonify(filters=filt), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/api/project/<int:project_id>', methods=['DELETE'])
def delete_project_endpoint(project_id):
    """
    DELETE /api/project/<id>
    Delete a saved project by its ID.
    """
    try:
        delete_project(project_id)
        return jsonify(message="Project deleted"), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    # Start the Flask development server on port 5000, accessible from any host
    app.run(debug=True, host='0.0.0.0', port=5000)
