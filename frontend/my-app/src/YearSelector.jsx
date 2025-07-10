import React from 'react';

// Компонент для выбора года
const YearSelector = ({ selectedYear, onYearChange, availableYears }) => {
  return (
    // Используем тот же класс-обертку, что и у других селекторов
    <div className="selector-wrapper">
      <label htmlFor="year-select">Год:</label>
      <select
        id="year-select"
        value={selectedYear}
        onChange={(e) => onYearChange(parseInt(e.target.value, 10))}
      >
        {availableYears.map(year => (
          <option key={year} value={year}>
            {year}
          </option>
        ))}
      </select>
    </div>
  );
};

export default YearSelector;