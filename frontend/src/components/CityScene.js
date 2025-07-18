// src/components/CityScene.js
import React, { useMemo } from 'react';
import { Box } from '@react-three/drei';
import * as THREE from 'three';

function CityScene({ buildings, onSelectBuilding, highlightedBuilding }) {
  const texture = useMemo(
    () =>
      new THREE.TextureLoader().load(
        'https://via.placeholder.com/100x100.png?text=Brick'
      ),
    []
  );
  const referencePoint = [-73.85, 40.86];
  const scaleFactor = 5000;

  if (!buildings || !Array.isArray(buildings)) {
    console.error('Invalid buildings data:', buildings);
    return null;
  }

  return (
    <group>
      {buildings.map(building => {
        const {
          id = Math.random(),
          geometry,
          height = 10,
          width = 10,
          length = 10,
        } = building;

        if (
          !geometry?.coordinates ||
          !Array.isArray(geometry.coordinates) ||
          geometry.coordinates.length !== 2
        ) {
          console.error(`Invalid coordinates for building ${id}:`, geometry);
          return null;
        }
        if (geometry.type !== 'Point') {
          console.error(`Invalid geometry for building ${id}: type is ${geometry.type}`, geometry);
          return null;
        }

        const [lon, lat] = geometry.coordinates;
        const x = (lon - referencePoint[0]) * scaleFactor;
        const z = (lat - referencePoint[1]) * scaleFactor;
        const y = Math.max(height, 5) / 2;

        const isSelected = highlightedBuilding?.id === id;
        const color = isSelected ? 'yellow' : 'orange';
        const scaleMult = isSelected ? 1.2 : 1.0;

        return (
          <Box
            key={id}
            position={[x, y, z]}
            args={[
              Math.max(width, 5) * scaleMult,
              Math.max(height, 5) * scaleMult,
              Math.max(length, 5) * scaleMult
            ]}
            onClick={e => {
              e.stopPropagation();
              onSelectBuilding(building);
            }}
            onPointerOver={e => (e.target.cursor = 'pointer')}
          >
            <meshStandardMaterial
              map={texture}
              color={color}
              emissive={color}
              emissiveIntensity={isSelected ? 0.3 : 0}
            />
          </Box>
        );
      })}
    </group>
  );
}

export default CityScene;
