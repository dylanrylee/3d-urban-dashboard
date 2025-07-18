import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Canvas, extend } from '@react-three/fiber';
import { FirstPersonControls } from '@react-three/drei';
import * as THREE from 'three';

import CityScene from './components/CityScene';
import QueryInput from './components/QueryInput';
import './App.css';

extend({ AxesHelper: THREE.AxesHelper });

function App() {
  const [allBuildings,    setAllBuildings]    = useState([]);
  const [displayed,       setDisplayed]       = useState([]);
  const [query,           setQuery]           = useState('');

  const [username,        setUsername]        = useState('');
  const [projectName,     setProjectName]     = useState('');
  const [projects,        setProjects]        = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [selectedBuilding,setSelectedBuilding]= useState(null);

  // Load all buildings once
  useEffect(() => {
    axios.get('http://localhost:5000/api/buildings')
      .then(res => {
        setAllBuildings(res.data);
        setDisplayed(res.data);
      })
      .catch(console.error);
  }, []);

  // Reload saved projects when username changes
  useEffect(() => {
    if (!username.trim()) {
      setProjects([]);
      setSelectedProject(null);
      return;
    }
    axios.get(`http://localhost:5000/api/projects/${username}`)
      .then(res => setProjects(res.data))
      .catch(console.error);
  }, [username]);

  // Run the LLM query (backend filters & returns matches)
  const handleQuery = async () => {
    if (!query.trim()) return;
    try {
      const res = await axios.post('http://localhost:5000/api/query', { query });
      if (res.data.error) {
        alert(res.data.error);
        return;
      }
      setDisplayed(res.data);
      setSelectedProject(null);
    } catch (err) {
      console.error(err);
      alert('Query failed');
    }
  };

  // Reset view
  const handleReset = () => {
    setDisplayed(allBuildings);
    setQuery('');
    setSelectedProject(null);
  };

  // Save current displayed as project
  const saveProject = async () => {
    if (!username.trim() || !projectName.trim()) {
      alert('Enter username & project name');
      return;
    }
    try {
      await axios.post('http://localhost:5000/api/projects', {
        username,
        projectName,
        filters: displayed.map(b => b.id),
      });
      const res = await axios.get(`http://localhost:5000/api/projects/${username}`);
      setProjects(res.data);
      alert('Project saved!');
    } catch (err) {
      console.error(err);
      alert('Save failed');
    }
  };

  // Load a project
  const loadProject = async (projId) => {
    if (!projId) return;
    try {
      const res = await axios.get(`http://localhost:5000/api/project/${projId}`);
      const ids = res.data.filters;
      setDisplayed(allBuildings.filter(b => ids.includes(b.id)));
      setSelectedProject(projId);
    } catch (err) {
      console.error(err);
      alert('Load failed');
    }
  };

  // Delete selected project
  const deleteProject = async () => {
    if (!selectedProject) return;
    if (!window.confirm('Delete this project?')) return;
    try {
      await axios.delete(`http://localhost:5000/api/project/${selectedProject}`);
      const res = await axios.get(`http://localhost:5000/api/projects/${username}`);
      setProjects(res.data);
      handleReset();
      alert('Project deleted');
    } catch (err) {
      console.error(err);
      alert('Delete failed');
    }
  };

  return (
    <div className="App">
      <h1>3D City Dashboard</h1>

      {/* Query Controls inside the box */}
      <div className="query-controls">
        <QueryInput
          query={query}
          setQuery={setQuery}
          onSubmit={handleQuery}
        />
        <button onClick={handleReset}>Reset View</button>
      </div>

      {/* Inline, horizontal instructions */}
      <ul className="instructions">
        <li><strong>WASD</strong> to move</li>
        <li><strong>RF</strong> to go up or down</li>
        <li><strong>Mouse</strong> to look</li>
        <li><strong>Click</strong> building for details</li>
        <li><strong>Run Query</strong> to filter</li>
        <li><strong>Reset</strong> to show all</li>
        <li><strong>Save/Load/Delete</strong> projects</li>
      </ul>

      {/* Project management */}
      <div className="project-controls">
        <input
          type="text"
          value={username}
          onChange={e => setUsername(e.target.value)}
          placeholder="Username"
        />
        <input
          type="text"
          value={projectName}
          onChange={e => setProjectName(e.target.value)}
          placeholder="Project Name"
        />
        <button onClick={saveProject}>Save Project</button>
        <select
          value={selectedProject || ''}
          onChange={e => loadProject(Number(e.target.value))}
        >
          <option value="">Load Project…</option>
          {projects.map(p => (
            <option key={p.id} value={p.id}>
              {p.name} ({p.filters.length})
            </option>
          ))}
        </select>
        <button
          onClick={deleteProject}
          disabled={!selectedProject}
        >
          Delete Project
        </button>
      </div>

      {/* 3D View */}
      <div className="scene-container">
        <Canvas className="Canvas" camera={{ position: [0,10,100], fov:45, near:0.1, far:20000 }}>
          <ambientLight intensity={1.0}/>
          <directionalLight position={[100,100,100]} intensity={1.5}/>

          <mesh position={[0,-0.1,0]} rotation={[-Math.PI/2,0,0]}>
            <planeGeometry args={[10000,10000]}/>
            <meshStandardMaterial color="green"/>
          </mesh>

          <primitive object={new THREE.AxesHelper(100)}/>
          <CityScene buildings={displayed} onSelectBuilding={setSelectedBuilding}/>
          <FirstPersonControls movementSpeed={200} lookSpeed={0.1} lookVertical/>
        </Canvas>

        {selectedBuilding && (
          <div className="details-panel">
            <h2>Building #{selectedBuilding.id}</h2>
            <p><strong>Height:</strong> {selectedBuilding.height} ft</p>
            <p><strong>Zoning:</strong> {selectedBuilding.zoning}</p>
            <button onClick={() => setSelectedBuilding(null)}>Close</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
