# 3D Urban Dashboard
### By: Dylan Rylee Dizon

An interactive 3D city‑block viewer for Calgary (or NYC by default) that lets you:

- Fetch building footprints, heights, zoning & more via open‑data APIs  
- Extrude & render them in Three.js  
- Click to highlight & show details  
- Run natural‑language filters powered by Google Gemini (or HF LLM)  
- Save/load/delete “projects” (filter‑sets) in SQLite  

---

## 🚀 Prerequisites

- **Git** (to clone the repo)  
- **Node.js** ≥ 14 & **npm** (for the React frontend)  
- **Python** ≥ 3.8 & **pip** (for the Flask backend)  

---

## Backend Setup

1. Clone and enter project root
   ```bash
   git clone https://github.com/your‑org/3d‑urban‑dashboard.git
   cd 3d‑urban‑dashboard
   ```

2. Create & activate a virtual environment\
   ```
   python3 -m venv .venv
   source .venv/bin/activate    # macOS/Linux
   .venv\Scripts\activate       # Windows PowerShell
   ```

3. Install Python dependencies
   ```
   pip install -r requirements.txt
   ```

4. Create a .env file in the project root with:
   ```
   GEMINI_API_KEY=your_google_gemini_api_key
   ```

5. Initialize the SQLite database
   ```
   python -c "import database; database.init_db()"
   ```

6. Run the Flask Server
   ```
   export FLASK_APP=app.py       # macOS/Linux
   set FLASK_APP=app.py          # Windows
   flask run --host=0.0.0.0 --port=5000
   ```

## Frontend Setup

1. Navigate into the React app
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies
   ```bash
   npm install
   ```

3. Create a .env file in the React folder with:
   ```
   REACT_APP_API_BASE=http://localhost:5000
   ```

4. Start the development server
   ```
   npm start
   ```
   
### Acknowledgements
- Uses Flask + google‑generativeai
- Uses React + @react‑three/fiber + @react‑three/drei

---
Feel free to tweak any paths or environment variables to match your setup!
