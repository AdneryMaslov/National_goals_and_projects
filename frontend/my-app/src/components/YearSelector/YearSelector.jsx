import React from 'react';
import styles from './YearSelector.module.css';

const YearSelector = ({ selectedYear, onYearChange, availableYears }) => {
  return (
    <div className={styles.selectorWrapper}>
      <label className={styles.label} htmlFor="year-select">Год:</label>
      <select
        id="year-select"
        className={styles.selectElement}
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
