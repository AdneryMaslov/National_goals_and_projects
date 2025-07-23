import React, { useState } from 'react';
import styles from './InformationDisplay.module.css';
import ProjectBudgetTable from '../ProjectBudgetTable/ProjectBudgetTable.jsx';
import IndicatorDisplay from '../IndicatorDisplay/IndicatorDisplay.jsx';
import MeasuresDisplay from '../MeasuresDisplay/MeasuresDisplay.jsx';
import YearSelector from '../YearSelector/YearSelector.jsx';
import LineChart from './LineChart/LineChart.jsx';
import RegionSelector from '../RegionSelector/RegionSelector.jsx';
import GoalSelector from '../GoalSelector/GoalSelector.jsx';
import ProjectSelector from '../ProjectSelector/ProjectSelector.jsx';
import TopPerformers from '../TopPerformers/TopPerformers.jsx';

// const API_URL = 'http://127.0.0.1:8000/api';
const API_URL = 'api';

const InformationDisplay = ({
  regions,
  goals,
  projects,
  selectedRegion,
  selectedGoal,
  selectedProject,
  onRegionSelect,
  onGoalSelect,
  onProjectSelect,
  projectDetails,
  selectedYear,
  onYearChange,
  availableYears,
  isLoading
}) => {
  const [modal, setModal] = useState({ isOpen: false, isLoading: true, indicatorName: '', historyData: null, chartType: 'yearly' });

  const handleShowChart = async (indicatorId, indicatorName) => {
    setModal({ isOpen: true, isLoading: true, indicatorName, historyData: null, chartType: 'yearly' });
    try {
      const response = await fetch(`${API_URL}/indicator/${indicatorId}/history?region_id=${selectedRegion.id}`);
      if (!response.ok) throw new Error(`Ошибка сервера: ${response.status}`);
      const data = await response.json();
      setModal(prev => ({ ...prev, isLoading: false, historyData: data }));
    } catch (error) {
      console.error("Не удалось загрузить данные для графика:", error);
      handleCloseModal();
    }
  };

  const handleCloseModal = () => { setModal({ isOpen: false, isLoading: false, indicatorName: '', historyData: null, chartType: 'yearly' }); };

  const getChartData = () => {
    if (!modal.historyData) return { labels: [], datasets: [] };
    const { historyData, chartType } = modal;
    const datasets = [];
    if (chartType === 'yearly') {
      const yearlyData = historyData.yearly_data || [];
      const referenceData = historyData.reference_data || [];
      const labels = yearlyData.map(d => d.date);

      if (referenceData.length > 0) {
        const referenceDataMap = new Map(referenceData.map(d => [d.date, d.value]));
        const alignedReferenceData = labels.map(label => {
          const value = referenceDataMap.get(label);
          if (value === undefined) return null;
          const numericMatch = String(value).match(/[\d\.,]+/);
          return numericMatch ? parseFloat(numericMatch[0].replace(',', '.')) : null;
        });
        datasets.push({
          label: 'Целевое значение',
          data: alignedReferenceData,
          borderColor: 'rgb(75, 192, 192)',
          borderDash: [5, 5],
          backgroundColor: 'rgba(75, 192, 192, 0.5)',
          tension: 0.1,
          borderWidth: 3,
          pointRadius: 4,
          pointBackgroundColor: 'rgb(75, 192, 192)',
        });
      }

      if (yearlyData.length > 0) {
        datasets.push({
          label: 'Фактическое значение',
          data: yearlyData.map(d => d.value),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
          tension: 0.1,
          borderWidth: 2,
        });
      }

      datasets.sort((a, b) => (a.label === 'Целевое значение' ? 1 : -1));

      return { labels, datasets };
    } else if (chartType === 'monthly') {
      const monthlyData = historyData.monthly_data || [];
      if (monthlyData.length > 0) datasets.push({ label: 'Месячные значения', data: monthlyData.map(d => ({ x: new Date(d.date), y: d.value })), borderColor: 'rgb(53, 162, 235)', backgroundColor: 'rgba(53, 162, 235, 0.5)' });
      return { datasets };
    }
    return { datasets: [] };
  };

  if (isLoading) {
    return <div className={styles.loaderContainer}><h2>Загрузка данных...</h2></div>;
  }
  if (!projectDetails) {
    return <div className={styles.loaderContainer}><p>Данные не найдены. Пожалуйста, выберите другие параметры.</p></div>;
  }

  return (
    <>
      <div className={styles.pageContainer}>
        <div className={styles.filtersHeader}>
          <RegionSelector regions={regions} selectedRegion={selectedRegion} onRegionSelect={onRegionSelect} />
          <GoalSelector goals={goals} selectedGoal={selectedGoal} onGoalSelect={onGoalSelect} />
          <ProjectSelector projects={projects} selectedProject={selectedProject} onProjectSelect={onProjectSelect} />
          <YearSelector selectedYear={selectedYear} onYearChange={onYearChange} availableYears={availableYears} />
        </div>

        {/* --- ИЗМЕНЕНИЕ ЗДЕСЬ: Новая структура --- */}
        <div className={styles.mainContentArea}>
          {/* Отдельный контейнер для верхнего ряда */}
          <div className={styles.topRow}>
            <div className={styles.gridBudget}>
                <ProjectBudgetTable budget={projectDetails.budget} selectedRegion={selectedRegion} />
            </div>
            <div className={styles.gridPerformers}>
                <TopPerformers metrics={projectDetails.metrics} />
            </div>
          </div>

          {/* Нижние блоки идут друг за другом */}
          <div className={styles.gridIndicators}>
              <IndicatorDisplay metrics={projectDetails.metrics} onShowChart={handleShowChart} />
          </div>
          <div className={styles.gridMeasures}>
              <MeasuresDisplay measures={projectDetails.activities} />
          </div>
        </div>
      </div>

      {modal.isOpen && (
        <div className={styles.modalOverlay} onClick={handleCloseModal}>
          <div className={styles.modalGraph} onClick={(e) => e.stopPropagation()}>
            <button onClick={handleCloseModal} className={styles.closeGraphButton}>×</button>
            <div className={styles.graphHeader}>
              <h5>Динамика: {modal.indicatorName}</h5>
            </div>
            {modal.isLoading ? (<p>Загрузка данных...</p>) : (
              <>
                <div className={styles.chartToggleButtons}>
                  <button onClick={() => setModal(prev => ({ ...prev, chartType: 'yearly' }))} className={modal.chartType === 'yearly' ? styles.active : ''} disabled={!modal.historyData?.yearly_data?.length}>По годам</button>
                  <button onClick={() => setModal(prev => ({ ...prev, chartType: 'monthly' }))} className={modal.chartType === 'monthly' ? styles.active : ''} disabled={!modal.historyData?.monthly_data?.length}>По месяцам</button>
                </div>
                <div className={styles.chartContainer}><LineChart chartData={getChartData()} title="" chartType={modal.chartType} /></div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
};
export default InformationDisplay;
