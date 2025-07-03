import React, { useState } from 'react';
import RegionSelector from './RegionSelector';
import GoalSelector from './GoalSelector'; // Новый компонент
import ProjectSelector from './ProjectSelector'; // Новый компонент
import InformationDisplay from './InformationDisplay';
import { mockData } from './mockData';
import './App.css';

function App() {
  const [step, setStep] = useState(1);
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [selectedGoal, setSelectedGoal] = useState(null); // Теперь хранит весь объект цели
  const [selectedProject, setSelectedProject] = useState(null); // Хранит весь объект проекта

  const availableRegions = Object.keys(mockData);

  const handleRegionSelect = (regionName) => {
    setSelectedRegion(mockData[regionName]);
    setStep(2);
  };

  const handleGoalSelect = (goal) => {
    setSelectedGoal(goal);
    setStep(3);
  };

  const handleProjectSelect = (project) => {
    setSelectedProject(project);
    setStep(4);
  };
  
  const handleReset = () => {
    setStep(1);
    setSelectedRegion(null);
    setSelectedGoal(null);
    setSelectedProject(null);
  };

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
          <h2>Шаг 2. Выберите национальную цель</h2>
          <GoalSelector goals={selectedRegion.goals} onGoalSelect={handleGoalSelect} />
        </div>
      )}

      {step === 3 && selectedGoal && (
        <div className="step-container">
          <h2>Шаг 3. Выберите национальный проект</h2>
          <p>Выбранная цель: <strong>{selectedGoal.name}</strong></p>
          <ProjectSelector projects={selectedGoal.projects} onProjectSelect={handleProjectSelect} />
        </div>
      )}
      
      {step === 4 && selectedProject && (
        <InformationDisplay
          regionName={Object.keys(mockData).find(key => mockData[key] === selectedRegion)}
          goalName={selectedGoal.name}
          project={selectedProject}
        />
      )}
    </div>
  );
}

export default App;
