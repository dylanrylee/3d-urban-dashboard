import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Canvas, extend } from '@react-three/fiber';
import { FirstPersonControls } from '@react-three/drei';
import * as THREE from 'three';
import CityScene from './components/CityScene';
import './App.css';

extend({ AxesHelper: THREE.AxesHelper });

function App() {
  const [buildings, setBuildings] = useState([]);
  const [query, setQuery] = useState('');
  const [username, setUsername] = useState('dylan');
  const [projectName, setProjectName] = useState('');
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:5000/api/buildings')
      .then(response => {
        console.log('Buildings data:', response.data);
        setBuildings(response.data);
      })
      .catch(error => {
        console.error('Error fetching buildings:', error);
      });
  }, []);

  const handleQuery = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/query', { query });
      const { attribute, operator, value } = response.data;
      const filtered = buildings.filter(b => {
        if (attribute === 'height') {
          return operator === '>' ? b.height > parseFloat(value) : b.height < parseFloat(value);
        }
        return true;
      });
      console.log('Queried buildings:', filtered);
      setBuildings(filtered);
    } catch (error) {
      console.error('Error querying:', error);
    }
  };

  const saveProject = async () => {
    try {
      await axios.post('http://localhost:5000/api/projects', {
        username,
        projectName,
        filters: buildings.map(b => b.id)
      });
      alert('Project saved!');
      fetchProjects();
    } catch (error) {
      console.error('Error saving project:', error);
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/projects/${username}`);
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const loadProject = async (projectId) => {
    try {
      const response = await axios.get(`http://localhost:5000/api/project/${projectId}`);
      const filterIds = response.data.filters;
      const filtered = buildings.filter(b => filterIds.includes(b.id));
      console.log('Loaded project buildings:', filtered);
      setBuildings(filtered);
      setSelectedProject(projectId);
    } catch (error) {
      console.error('Error loading project:', error);
    }
  };

  return (
    <div className="App">
      <h1>Urban Design 3D City Dashboard</h1>
      <div className="controls">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Enter query (e.g., highlight buildings over 10 feet)"
        />
        <button onClick={handleQuery}>Run Query</button>
        <input
          type="text"
          value={projectName}
          onChange={e => setProjectName(e.target.value)}
          placeholder="Project Name"
        />
        <button onClick={saveProject}>Save Project</button>
        <select onChange={e => loadProject(e.target.value)} value={selectedProject || ''}>
          <option value="">Select Project</option>
          {projects.map(project => (
            <option key={project.id} value={project.id}>{project.name}</option>
          ))}
        </select>
      </div>
      <Canvas camera={{ position: [0, 10, 100], fov: 45, near: 0.1, far: 20000 }}>
        <ambientLight intensity={1.0} />
        <directionalLight position={[100, 100, 100]} intensity={1.5} />
        <mesh position={[0, -0.1, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <planeGeometry args={[10000, 10000]} />
          <meshStandardMaterial color="green" />
        </mesh>
        <primitive object={new THREE.AxesHelper(100)} />
        <CityScene buildings={buildings} />
        <FirstPersonControls
          movementSpeed={200}
          lookSpeed={0.1}
          lookVertical={true}
        />
      </Canvas>
    </div>
  );
}

export default App;