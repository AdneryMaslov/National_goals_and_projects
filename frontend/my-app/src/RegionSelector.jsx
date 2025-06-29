import React from 'react';

// Теперь компонент принимает список регионов как пропс
const RegionSelector = ({ regions, onRegionSelect }) => {
  return (
    <div>
      <select
        defaultValue=""
        onChange={e => onRegionSelect(e.target.value)}
      >
        <option value="" disabled>-- Выберите регион --</option>
        {regions.map(region => (
          <option key={region} value={region}>{region}</option>
        ))}
      </select>
    </div>
  );
};

export default RegionSelector;
