from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
import json

from database import (
    init_db,
    save_project,
    load_projects,        # returns only id + project_name
    get_project_filters,  # returns raw filters array
    delete_project
)
from data_fetcher import fetch_calgary_data
from llm_processor import process_query

app = Flask(__name__)
CORS(app)
init_db()

@app.route('/api/buildings', methods=['GET'])
def get_buildings():
    try:
        return jsonify(fetch_calgary_data())
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/api/query', methods=['POST'])
def query_buildings():
    payload = request.json or {}
    q = payload.get('query', '').strip()
    if not q:
        return jsonify(error="Query is required"), 400

    criteria = process_query(q)
    if 'error' in criteria:
        return jsonify(error=criteria['error'], raw=criteria.get('raw')), 400

    try:
        buildings = fetch_calgary_data()
    except Exception as e:
        return jsonify(error=str(e)), 500

    def matches(b):
        attr = criteria.get('attribute')
        op   = criteria.get('operator')
        val  = criteria.get('value')
        bval = b.get(attr)
        if bval is None:
            return False
        try:
            if   op == '>':   return bval >  val
            elif op == '<':   return bval <  val
            elif op == '>=':  return bval >= val
            elif op == '<=':  return bval <= val
            elif op == '==':
                if isinstance(bval, str):
                    return bval.lower() == str(val).lower()
                return bval == val
        except:
            return False
        return False

    return jsonify([b for b in buildings if matches(b)]), 200

@app.route('/api/projects', methods=['POST'])
def save_project_endpoint():
    data = request.json or {}
    user = data.get('username', '').strip()
    name = data.get('projectName', '').strip()
    filters = data.get('filters')  # expect array of IDs

    if not user or not name:
        return jsonify(error="username and projectName are required"), 400
    if not isinstance(filters, list):
        return jsonify(error="filters must be a list"), 400

    save_project(user, name, json.dumps(filters))
    return jsonify(message="Project saved"), 200

@app.route('/api/projects/<username>', methods=['GET'])
def load_projects_endpoint(username):
    try:
        # Returns [ { id, name }, … ]
        return jsonify(load_projects(username)), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/api/project/<int:project_id>', methods=['GET'])
def load_project_filters(project_id):
    try:
        filt = get_project_filters(project_id)
        if filt is None:
            return jsonify(error="Project not found"), 404
        # Return under a key so frontend can do res.data.filters
        return jsonify(filters=filt), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/api/project/<int:project_id>', methods=['DELETE'])
def delete_project_endpoint(project_id):
    try:
        delete_project(project_id)
        return jsonify(message="Project deleted"), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
