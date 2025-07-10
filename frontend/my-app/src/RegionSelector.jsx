import React from 'react';

const RegionSelector = ({ regions, selectedRegion, onRegionSelect }) => {
  const handleSelect = (e) => {
    const regionId = e.target.value;
    const selectedRegionObject = regions.find(r => r.id === parseInt(regionId));
    onRegionSelect(selectedRegionObject);
  };

  return (
    <div className="selector-wrapper">
      <label>Регион:</label>
      <select value={selectedRegion?.id || ''} onChange={handleSelect}>
        <option value="" disabled>-- Выберите регион --</option>
        {regions.map(region => (
          <option key={region.id} value={region.id}>
            {region.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default RegionSelector;