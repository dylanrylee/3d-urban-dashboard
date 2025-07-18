import React, { useMemo } from 'react';
import { Box } from '@react-three/drei';
import * as THREE from 'three';

function CityScene({ buildings }) {
  const texture = useMemo(() => new THREE.TextureLoader().load('https://via.placeholder.com/100x100.png?text=Brick'), []);
  const referencePoint = [-73.85, 40.86];
  const scaleFactor = 5000;

  if (!buildings || !Array.isArray(buildings)) {
    console.error('Invalid buildings data:', buildings);
    return null;
  }

  const positions = buildings.map(building => {
    const { geometry } = building;
    if (geometry?.coordinates) {
      const [lon, lat] = geometry.coordinates;
      return { x: (lon - referencePoint[0]) * scaleFactor, z: (lat - referencePoint[1]) * scaleFactor };
    }
    return null;
  }).filter(pos => pos);
  console.log('Building position ranges:', {
    x: { min: Math.min(...positions.map(p => p.x)), max: Math.max(...positions.map(p => p.x)) },
    z: { min: Math.min(...positions.map(p => p.z)), max: Math.max(...positions.map(p => p.z)) }
  });

  return (
    <group>
      {buildings.map(building => {
        const { id = Math.random(), geometry, height = 10, width = 10, length = 10, zoning = 'gray' } = building;

        if (!geometry?.coordinates || !Array.isArray(geometry.coordinates) || geometry.coordinates.length !== 2) {
          console.error(`Invalid coordinates for building ${id}:`, geometry);
          return null;
        }
        if (geometry.type !== 'Point') {
          console.error(`Invalid geometry for building ${id}: type is ${geometry.type}`, geometry);
          return null;
        }
        if (height <= 0) {
          console.warn(`Non-positive height for building ${id}, using default:`, height);
        }

        const [lon, lat] = geometry.coordinates;
        const x = (lon - referencePoint[0]) * scaleFactor;
        const z = (lat - referencePoint[1]) * scaleFactor;
        const y = Math.max(height, 5) / 2;
        console.log(`Building ${id} position: [${x}, ${y}, ${z}], dimensions: [${width}, ${height}, ${length}]`);
        const color = zoning === 'R6' ? 'red' : zoning === 'C4-4A' ? 'blue' : zoning === 'Residential' ? 'orange' : 'yellow';
        return (
          <Box
            key={id}
            position={[x, y, z]}
            args={[Math.max(width, 5), Math.max(height, 5), Math.max(length, 5)]}
          >
            <meshStandardMaterial color={color} />
          </Box>
        );
      })}
    </group>
  );
}

export default CityScene;