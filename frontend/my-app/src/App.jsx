import React, { useState, useEffect } from 'react';
import RegionSelector from './RegionSelector';
import GoalSelector from './GoalSelector';
import ProjectSelector from './ProjectSelector';
import InformationDisplay from './InformationDisplay';
import logo from '/logo.jpg'; // Убедитесь, что лого в папке 'public'
import './App.css';

const API_URL = 'http://127.0.0.1:8000/api';

function App() {
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  const [regions, setRegions] = useState([]);
  const [goals, setGoals] = useState([]);
  const [projects, setProjects] = useState([]);

  const [selectedRegion, setSelectedRegion] = useState(null);
  const [selectedGoal, setSelectedGoal] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);

  const [selectedYear, setSelectedYear] = useState(2024);

  const [projectDetails, setProjectDetails] = useState(null);

  useEffect(() => {
    const fetchRegions = async () => {
      try {
        const response = await fetch(`${API_URL}/regions`);
        if (!response.ok) throw new Error('Ошибка при загрузке регионов');
        const data = await response.json();
        setRegions(data);
      } catch (error) { console.error(error); }
    };
    fetchRegions();
  }, []);

  useEffect(() => {
    if (selectedRegion) {
      const fetchGoals = async () => {
        try {
          const response = await fetch(`${API_URL}/goals`);
          if (!response.ok) throw new Error('Ошибка при загрузке нац. целей');
          const data = await response.json();
          setGoals(data);
          setStep(2);
        } catch (error) { console.error(error); }
      };
      fetchGoals();
    }
  }, [selectedRegion]);

  useEffect(() => {
    if (selectedGoal) {
      const fetchProjects = async () => {
        try {
          const response = await fetch(`${API_URL}/goals/${selectedGoal.id}/projects`);
          if (!response.ok) throw new Error('Ошибка при загрузке проектов');
          const data = await response.json();
          setProjects(data);
          setStep(3);
        } catch (error) { console.error(error); }
      };
      fetchProjects();
    }
  }, [selectedGoal]);

  useEffect(() => {
    if (selectedRegion && selectedGoal && selectedProject) {
      const fetchProjectDetails = async () => {
        setIsLoading(true);
        setStep(4);
        try {
          const url = `${API_URL}/data?region_id=${selectedRegion.id}&goal_id=${selectedGoal.id}&project_id=${selectedProject.id}&year=${selectedYear}`;
          const response = await fetch(url);
          if (!response.ok) throw new Error('Ошибка при загрузке детальной информации');
          const data = await response.json();
          setProjectDetails(data);
        } catch (error) {
          console.error(error);
          setProjectDetails(null);
        } finally {
          setIsLoading(false);
        }
      };
      fetchProjectDetails();
    }
  }, [selectedRegion, selectedGoal, selectedProject, selectedYear]);

  const handleRegionSelect = (region) => {
    setSelectedRegion(region);
    setSelectedGoal(null);
    setSelectedProject(null);
    setProjects([]);
  };

  const handleGoalSelect = (goal) => {
    setSelectedGoal(goal);
    setSelectedProject(null);
  };

  const handleProjectSelect = (project) => {
    setSelectedProject(project);
  };

  const handleYearChange = (year) => setSelectedYear(year);

  const handleReset = () => {
    setStep(1);
    setIsLoading(false);
    setSelectedRegion(null);
    setSelectedGoal(null);
    setProjects([]);
    setSelectedProject(null);
    setProjectDetails(null);
    setSelectedYear(2024);
  };

  return (
    <div className="App">
      <header className="main-app-header">
        <img src={logo} alt="Логотип проекта" className="logo" />
        <h1 className="app-title">Анализ национальных целей</h1>
        {step === 4 && <button onClick={handleReset} className="reset-button">Начать заново</button>}
      </header>

      <main className="main-content">
        {step < 4 && (
          <>
            {step === 1 && (
              <div className="step-container">
                <h2>Шаг 1. Выберите регион</h2>
                <RegionSelector regions={regions} onRegionSelect={handleRegionSelect} selectedRegion={selectedRegion} />
              </div>
            )}
            {step === 2 && (
              <div className="step-container">
                <h2>Шаг 2. Выберите национальную цель</h2>
                <GoalSelector goals={goals} onGoalSelect={handleGoalSelect} selectedGoal={selectedGoal} />
              </div>
            )}
            {step === 3 && (
              <div className="step-container">
                <h2>Шаг 3. Выберите национальный проект</h2>
                <ProjectSelector projects={projects} onProjectSelect={handleProjectSelect} selectedProject={selectedProject} />
              </div>
            )}
          </>
        )}

        {step === 4 && (
          <InformationDisplay
            regions={regions}
            goals={goals}
            projects={projects}
            selectedRegion={selectedRegion}
            selectedGoal={selectedGoal}
            selectedProject={selectedProject}
            onRegionSelect={handleRegionSelect}
            onGoalSelect={handleGoalSelect}
            onProjectSelect={handleProjectSelect}
            projectDetails={projectDetails}
            selectedYear={selectedYear}
            onYearChange={handleYearChange}
            availableYears={[2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]}
            isLoading={isLoading}
          />
        )}
      </main>
    </div>
  );
}

export default App;