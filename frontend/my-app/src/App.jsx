import React, { useState } from 'react';
import RegionSelector from './RegionSelector';
import GoalProjectSelector from './GoalProjectSelector';
import InformationDisplay from './InformationDisplay';
import { mockData } from './mockData'; // Импортируем наши данные
import './App.css';

function App() {
  const [step, setStep] = useState(1);
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [selection, setSelection] = useState(null); // { type: 'goal'/'project', value: '...' }

  // Получаем список регионов из ключей нашего объекта данных
  const availableRegions = Object.keys(mockData);

  const handleRegionSelect = (region) => {
    setSelectedRegion(region);
    setStep(2);
  };

  const handleGoalOrProjectSelect = (selected) => {
    setSelection(selected);
    setStep(3);
  };

  const handleReset = () => {
    setStep(1);
    setSelectedRegion(null);
    setSelection(null);
  };
  
  // Функция для получения данных на основе выбора
  const getFinalData = () => {
    if (!selectedRegion || !selection) return null;
    
    // type может быть 'goals' или 'projects'
    const { type, value } = selection;
    const selectionTypeKey = type === 'goal' ? 'goals' : 'projects';
    
    return mockData[selectedRegion]?.[selectionTypeKey]?.[value];
  }

  return (
    <div className="App">
      <header className="app-header">
        <h1>Анализ национальных целей</h1>
        {step > 1 && <button onClick={handleReset} className="reset-button">Начать заново</button>}
      </header>

      {step === 1 && (
        <div className="step-container">
          <h2>Шаг 1. Выберите регион</h2>
          <RegionSelector regions={availableRegions} onRegionSelect={handleRegionSelect} />
        </div>
      )}

      {step === 2 && selectedRegion && (
        <div className="step-container">
          <h2>Шаг 2. Выберите цель или проект</h2>
          <p>Выбранный регион: <strong>{selectedRegion}</strong></p>
          <GoalProjectSelector
            // Передаем доступные цели и проекты для выбранного региона
            availableGoals={Object.keys(mockData[selectedRegion].goals)}
            availableProjects={Object.keys(mockData[selectedRegion].projects)}
            onGoalOrProjectSelect={handleGoalOrProjectSelect}
          />
        </div>
      )}

      {step === 3 && selection && (
        <InformationDisplay
          region={selectedRegion}
          selection={selection}
          data={getFinalData()} // Передаем отфильтрованные данные
        />
      )}
    </div>
  );
}

export default App;
