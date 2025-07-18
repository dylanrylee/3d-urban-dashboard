import React, { useMemo } from 'react';
import { Box } from '@react-three/drei';
import * as THREE from 'three';

function CityScene({ buildings }) {
  const texture = useMemo(() => new THREE.TextureLoader().load('https://via.placeholder.com/100x100.png?text=Brick'), []);

  return (
    <group>
      {buildings.map(building => {
        const { id, geometry, height, width = 20, length = 25, zoning } = building;
        if (geometry.type !== 'Point') {
          console.error(`Invalid geometry for building ${id}:`, geometry);
          return null;
        }
        const [x, z] = geometry.coordinates;
        const y = 0; // Base of cube at ground level, height extends upward
        const color = zoning === 'R6' ? 'red' : zoning === 'C4-4A' ? 'blue' : 'gray';
        return (
          <Box
            key={id}
            position={[x, y, z]}
            args={[width / 10000, height, length / 10000]} // Adjusted scale
          >
            <meshStandardMaterial map={texture} color={color} />
          </Box>
        );
      })}
    </group>
  );
}

export default CityScene;