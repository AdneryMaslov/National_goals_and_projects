import React, { useState, useEffect } from 'react';
import RegionSelector from '../RegionSelector/RegionSelector.jsx';
import GoalSelector from '../GoalSelector/GoalSelector.jsx';
import ProjectSelector from '../ProjectSelector/ProjectSelector.jsx';
import InformationDisplay from '../InformationDisplay/InformationDisplay.jsx';
import logo from '/logo.jpg'; // Убедитесь, что логотип в папке 'public'
import styles from './App.module.css';

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
    const fetchRegions = async () => { try { const response = await fetch(`${API_URL}/regions`); if (!response.ok) throw new Error('Ошибка загрузки регионов'); const data = await response.json(); setRegions(data); } catch (error) { console.error(error); } };
    fetchRegions();
  }, []);

  useEffect(() => {
    if (selectedRegion) { const fetchGoals = async () => { try { const response = await fetch(`${API_URL}/goals`); if (!response.ok) throw new Error('Ошибка загрузки нац. целей'); const data = await response.json(); setGoals(data); setStep(2); } catch (error) { console.error(error); } }; fetchGoals(); }
  }, [selectedRegion]);

  useEffect(() => {
    if (selectedGoal) { const fetchProjects = async () => { try { const response = await fetch(`${API_URL}/goals/${selectedGoal.id}/projects`); if (!response.ok) throw new Error('Ошибка загрузки проектов'); const data = await response.json(); setProjects(data); setStep(3); } catch (error) { console.error(error); } }; fetchProjects(); }
  }, [selectedGoal]);

  useEffect(() => {
    if (selectedRegion && selectedGoal && selectedProject) { const fetchProjectDetails = async () => { setIsLoading(true); setStep(4); try { const url = `${API_URL}/data?region_id=${selectedRegion.id}&goal_id=${selectedGoal.id}&project_id=${selectedProject.id}&year=${selectedYear}`; const response = await fetch(url); if (!response.ok) throw new Error('Ошибка загрузки детальной информации'); const data = await response.json(); setProjectDetails(data); } catch (error) { console.error(error); setProjectDetails(null); } finally { setIsLoading(false); } }; fetchProjectDetails(); }
  }, [selectedRegion, selectedGoal, selectedProject, selectedYear]);

  const handleRegionSelect = (region) => { setSelectedRegion(region); setSelectedGoal(null); setSelectedProject(null); setProjects([]); };
  const handleGoalSelect = (goal) => { setSelectedGoal(goal); setSelectedProject(null); };
  const handleProjectSelect = (project) => { setSelectedProject(project); };
  const handleYearChange = (year) => setSelectedYear(year);
  const handleReset = () => { setStep(1); setIsLoading(false); setSelectedRegion(null); setSelectedGoal(null); setProjects([]); setSelectedProject(null); setProjectDetails(null); setSelectedYear(2024); };

  return (
    <div className={styles.App}>
      {/* 1. Единая шапка для всего приложения */}
      <header className={styles.mainAppHeader}>
        {/* 2. Обертка для лого и заголовка, которая вызывает сброс по клику */}
        <div className={styles.logoTitleWrapper} onClick={handleReset} role="button" tabIndex="0">
          <img src={logo} alt="Логотип проекта" className={styles.logo} />
          <h1 className={styles.appTitle}>Анализ национальных целей</h1>
        </div>
      </header>

      <main className={styles.mainContent}>
        {step < 4 ? (
          <div className={styles.stepContainer}>
            {step === 1 && ( <> <h2>Шаг 1. Выберите регион</h2> <RegionSelector regions={regions} onRegionSelect={handleRegionSelect} selectedRegion={selectedRegion} /> </> )}
            {step === 2 && ( <> <h2>Шаг 2. Выберите национальную цель</h2> <GoalSelector goals={goals} onGoalSelect={handleGoalSelect} selectedGoal={selectedGoal} /> </> )}
            {step === 3 && ( <> <h2>Шаг 3. Выберите национальный проект</h2> <ProjectSelector projects={projects} onProjectSelect={handleProjectSelect} selectedProject={selectedProject} /> </> )}
          </div>
        ) : (
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
