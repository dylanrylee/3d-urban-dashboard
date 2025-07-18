// src/App.js
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
  const [allBuildings, setAllBuildings]       = useState([]);
  const [displayed,   setDisplayed]           = useState([]);
  const [query,       setQuery]               = useState('');
  const [username,    setUsername]            = useState('dylan');
  const [projectName, setProjectName]         = useState('');
  const [projects,    setProjects]            = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [selectedBuilding, setSelectedBuilding]= useState(null);

  // fetch once
  useEffect(() => {
    axios.get('http://localhost:5000/api/buildings')
      .then(res => {
        setAllBuildings(res.data);
        setDisplayed(res.data);
      })
      .catch(console.error);
  }, []);

  // now just ask back-end for filtered list
  const handleQuery = async () => {
    try {
      const res = await axios.post('http://localhost:5000/api/query', { query });
      if (res.data.error) {
        alert(res.data.error);
        return;
      }
      console.log('Filtered from server:', res.data.map(b => b.id));
      setDisplayed(res.data);
    } catch (err) {
      console.error(err);
      alert('Query failed — see console');
    }
  };

  // reset to full set
  const handleReset = () => {
    setDisplayed(allBuildings);
    setQuery('');
  };

  // save/load code unchanged (but now uses displayed)
  const saveProject = async () => {
    await axios.post('http://localhost:5000/api/projects', {
      username,
      projectName,
      filters: displayed.map(b => b.id)
    });
    fetchProjects();
  };
  const fetchProjects = async () => {
    const res = await axios.get(`http://localhost:5000/api/projects/${username}`);
    setProjects(res.data);
  };
  const loadProject = async id => {
    const res = await axios.get(`http://localhost:5000/api/project/${id}`);
    const ids = res.data.filters.matchedIds || [];
    setDisplayed(allBuildings.filter(b => ids.includes(b.id)));
    setSelectedProject(id);
  };

  return (
    <div className="App">
      <h1>3D City Dashboard</h1>
      <div className="controls">
        <input
          value={username}
          onChange={e => setUsername(e.target.value)}
          placeholder="Username"
        />

        <QueryInput
          query={query}
          setQuery={setQuery}
          onSubmit={handleQuery}
        />

        <button onClick={handleReset}>Reset</button>

        <input
          value={projectName}
          onChange={e => setProjectName(e.target.value)}
          placeholder="Project Name"
        />
        <button onClick={saveProject}>Save Project</button>

        <select onChange={e => loadProject(Number(e.target.value))} value={selectedProject || ''}>
          <option value="">Load Project…</option>
          {projects.map(p => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
      </div>

      <div className="scene-container">
        <Canvas camera={{ position: [0,10,100], fov:45, near:0.1, far:20000 }}>
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
