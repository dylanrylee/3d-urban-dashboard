import sqlite3
import json

# Initialize the SQLite database and ensure the "projects" table exists
def init_db():
    # Connect to (or create) the `projects.db` SQLite database file
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    # Create the "projects" table if it doesn't already exist
    c.execute('''
      CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  # Auto-incrementing project ID
        username TEXT,                         # Owner of the project
        project_name TEXT,                     # Human-readable project name
        filters TEXT                           # JSON-encoded list of building IDs
      )
    ''')
    conn.commit()  # Save changes
    conn.close()   # Close the connection

# Save a new project record for a given user
def save_project(username, project_name, filters):
    # Connect to the database
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    # Insert a new row into "projects" with provided username, project_name, and filters JSON
    c.execute(
      'INSERT INTO projects (username, project_name, filters) VALUES (?, ?, ?)',
      (username, project_name, filters)
    )
    conn.commit()  # Commit the insertion
    conn.close()   # Close the connection

# Load all projects belonging to a specific user
def load_projects(username):
    # Connect to the database
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    # Query for id, project_name, and filters JSON for the given username
    c.execute(
      'SELECT id, project_name, filters FROM projects WHERE username = ?',
      (username,)
    )
    projects = []
    # Iterate over each row returned
    for proj_id, proj_name, filters_json in c.fetchall():
        try:
            # Attempt to decode the filters JSON string into a Python list
            filt = json.loads(filters_json)
        except json.JSONDecodeError:
            # Fallback to an empty list if JSON is malformed
            filt = []
        # Append a dict for each project with parsed filters
        projects.append({
            "id": proj_id,
            "name": proj_name,
            "filters": filt
        })
    conn.close()  # Close the connection
    return projects

# Retrieve the raw filters list for a single project by its ID
def get_project_filters(project_id):
    # Connect to the database
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    # Select the filters JSON for the specific project ID
    c.execute(
      'SELECT filters FROM projects WHERE id = ?',
      (project_id,)
    )
    row = c.fetchone()
    conn.close()  # Close the connection
    # If a row was found, decode its JSON; otherwise return None
    return json.loads(row[0]) if row else None

# Delete a project record by its ID
def delete_project(project_id):
    """
    Remove a project from the database by its ID.
    """
    # Connect to the database
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    # Execute the delete statement
    c.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()  # Commit the deletion
    conn.close()   # Close the connection
