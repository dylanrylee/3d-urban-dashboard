import sqlite3
import json

def init_db():
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  project_name TEXT,
                  filters TEXT)''')
    conn.commit()
    conn.close()

def save_project(username, project_name, filters):
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute('INSERT INTO projects (username, project_name, filters) VALUES (?, ?, ?)',
              (username, project_name, filters))
    conn.commit()
    conn.close()

def load_projects(username):
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute('SELECT id, project_name FROM projects WHERE username = ?', (username,))
    projects = [{"id": row[0], "name": row[1]} for row in c.fetchall()]
    conn.close()
    return projects

def get_project_filters(project_id):
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute('SELECT filters FROM projects WHERE id = ?', (project_id,))
    result = c.fetchone()
    conn.close()
    return json.loads(result[0]) if result else []