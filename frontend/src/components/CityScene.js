import React, { useMemo } from 'react';
import { Box } from '@react-three/drei';
import * as THREE from 'three';

function CityScene({ buildings }) {
  const texture = useMemo(() => new THREE.TextureLoader().load('https://via.placeholder.com/100x100.png?text=Brick'), []);
  const referencePoint = [-73.85, 40.86]; // Matches your data

  if (!buildings || !Array.isArray(buildings)) {
    console.error('Invalid buildings data:', buildings);
    return null;
  }

  return (
    <group>
      <Box position={[0, 5, 0]} args={[10, 10, 10]}>
        <meshStandardMaterial color="yellow" />
      </Box>
      {buildings.map(building => {
        const { id = Math.random(), geometry, height = 10, width = 10, length = 10, zoning = 'gray' } = building;

        if (!geometry?.coordinates || height <= 0) {
          console.error(`Missing or invalid data for building ${id}:`, building);
          return null;
        }
        if (geometry.type !== 'Point') {
          console.error(`Invalid geometry for building ${id}: type is ${geometry.type}`, geometry);
          return null;
        }

        const [lon, lat] = geometry.coordinates;
        const x = (lon - referencePoint[0]) * 10000; // Increased to 10000
        const z = (lat - referencePoint[1]) * 10000;
        const y = height / 2;
        console.log(`Building ${id} position: [${x}, ${y}, ${z}], dimensions: [${width}, ${height}, ${length}]`);
        const color = zoning === 'R6' ? 'red' : zoning === 'C4-4A' ? 'blue' : zoning === 'Residential' ? 'orange' : 'gray';
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