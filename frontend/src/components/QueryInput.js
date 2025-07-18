// src/components/QueryInput.js
import React from 'react';

export default function QueryInput({ query, setQuery, onSubmit }) {
  return (
    <div className="query-input">
      <input
        type="text"
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="e.g., show residential buildings"
      />
      <button onClick={onSubmit}>Run Query</button>
    </div>
  );
}
