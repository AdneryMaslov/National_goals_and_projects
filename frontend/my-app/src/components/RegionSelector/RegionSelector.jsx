import React from 'react';
import SearchableSelector from '../SearchableSelector/SearchableSelector.jsx';

const RegionSelector = ({ regions, selectedRegion, onRegionSelect }) => {
  return (
    <SearchableSelector
      options={regions}
      value={selectedRegion}
      onChange={onRegionSelect}
      label="Регион:"
      placeholder="-- Введите или выберите регион --"
    />
  );
};

export default RegionSelector;
