from flask import Flask, request, jsonify
from flask_cors import CORS
from database import init_db, save_project, load_projects, get_project_filters
from llm_processor import process_query
from data_fetcher import fetch_calgary_data
import json

app = Flask(__name__)
CORS(app)  # Enable CORS to allow frontend requests from a different origin (e.g., localhost:3000)

@app.route('/api/buildings', methods=['GET'])
def get_buildings():
    """
    Fetch building data from Calgary Open Data API.
    Returns a JSON list of buildings with id, geometry, height, address, zoning, and value.
    """
    try:
        buildings = fetch_calgary_data()
        return jsonify(buildings)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch building data: {str(e)}"}), 500

@app.route('/api/query', methods=['POST'])
def query_buildings():
    """
    Process a natural language query using the Hugging Face LLM API.
    Expects JSON payload with 'query' field (e.g., {"query": "highlight buildings over 100 feet"}).
    Returns JSON with filter details (attribute, operator, value) or error.
    """
    try:
        query = request.json.get('query')
        if not query:
            return jsonify({"error": "Query is required"}), 400
        result = process_query(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Failed to process query: {str(e)}"}), 500

@app.route('/api/projects', methods=['POST'])
def save_project_endpoint():
    """
    Save a project with username, project name, and filters.
    Expects JSON payload with 'username', 'projectName', and 'filters'.
    """
    try:
        data = request.json
        username = data.get('username')
        project_name = data.get('projectName')
        filters = json.dumps(data.get('filters', []))
        if not username or not project_name:
            return jsonify({"error": "Username and project name are required"}), 400
        save_project(username, project_name, filters)
        return jsonify({"message": "Project saved successfully"})
    except Exception as e:
        return jsonify({"error": f"Failed to save project: {str(e)}"}), 500

@app.route('/api/projects/<username>', methods=['GET'])
def load_projects_endpoint(username):
    """
    Load all projects for a given username.
    Returns a JSON list of projects with id and name.
    """
    try:
        projects = load_projects(username)
        return jsonify(projects)
    except Exception as e:
        return jsonify({"error": f"Failed to load projects: {str(e)}"}), 500

@app.route('/api/project/<project_id>', methods=['GET'])
def load_project_filters(project_id):
    """
    Load filters for a specific project by ID.
    Returns JSON with the project's filters.
    """
    try:
        filters = get_project_filters(project_id)
        return jsonify({"filters": filters})
    except Exception as e:
        return jsonify({"error": f"Failed to load project filters: {str(e)}"}), 500

if __name__ == '__main__':
    init_db()  # Initialize SQLite database
    app.run(debug=True, host='0.0.0.0', port=5000)