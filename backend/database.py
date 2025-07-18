import sqlite3
import json

def init_db():
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute('''
      CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        project_name TEXT,
        filters TEXT
      )
    ''')
    conn.commit()
    conn.close()

def save_project(username, project_name, filters):
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute(
      'INSERT INTO projects (username, project_name, filters) VALUES (?, ?, ?)',
      (username, project_name, filters)
    )
    conn.commit()
    conn.close()

def load_projects(username):
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute(
      'SELECT id, project_name, filters FROM projects WHERE username = ?',
      (username,)
    )
    projects = []
    for proj_id, proj_name, filters_json in c.fetchall():
        try:
            filt = json.loads(filters_json)
        except json.JSONDecodeError:
            filt = []
        projects.append({
            "id": proj_id,
            "name": proj_name,
            "filters": filt
        })
    conn.close()
    return projects

def get_project_filters(project_id):
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute(
      'SELECT filters FROM projects WHERE id = ?',
      (project_id,)
    )
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None

def delete_project(project_id):
    """
    Remove a project from the database by its ID.
    """
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()
