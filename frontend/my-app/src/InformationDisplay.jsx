import React, { useState } from 'react';
import ProjectBudgetTable from './ProjectBudgetTable'; // 1. Импортируем новый компонент
import IndicatorDisplay from './IndicatorDisplay';
import MeasuresDisplay from './MeasuresDisplay';
import YearSelector from './YearSelector';
import LineChart from './LineChart';
import RegionSelector from './RegionSelector';
import GoalSelector from './GoalSelector';
import ProjectSelector from './ProjectSelector';
import logo from '/logo.jpg';

const API_URL = 'http://127.0.0.1:8000/api';

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
  isLoading,
  onReset
}) => {
  const [modal, setModal] = useState({
    isOpen: false,
    isLoading: true,
    indicatorName: '',
    historyData: null,
    chartType: 'yearly'
  });

  const handleShowChart = async (indicatorId, indicatorName) => {
    setModal({ isOpen: true, isLoading: true, indicatorName, historyData: null, chartType: 'yearly' });
    try {
      const response = await fetch(`${API_URL}/indicator/${indicatorId}/history?region_id=${selectedRegion.id}`);
      if (!response.ok) {
        throw new Error(`Ошибка сервера: ${response.status}`);
      }
      const data = await response.json();
      setModal(prev => ({ ...prev, isLoading: false, historyData: data }));
    } catch (error) {
      console.error("Не удалось загрузить данные для графика:", error);
      handleCloseModal();
    }
  };

  const handleCloseModal = () => {
    setModal({ isOpen: false, isLoading: false, indicatorName: '', historyData: null, chartType: 'yearly' });
  };

  const getChartData = () => {
    if (!modal.historyData) {
      return { labels: [], datasets: [] };
    }
    const { historyData, chartType } = modal;
    const datasets = [];
    if (chartType === 'yearly') {
      const yearlyData = historyData.yearly_data || [];
      const referenceData = historyData.reference_data || [];
      const labels = yearlyData.map(d => d.date);
      if (yearlyData.length > 0) {
        datasets.push({
          label: 'Фактическое значение',
          data: yearlyData.map(d => d.value),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
          tension: 0.1,
        });
      }
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
        });
      }
      return { labels, datasets };
    } else if (chartType === 'monthly') {
      const monthlyData = historyData.monthly_data || [];
      if (monthlyData.length > 0) {
        datasets.push({
          label: 'Месячные значения',
          data: monthlyData.map(d => ({ x: new Date(d.date), y: d.value })),
          borderColor: 'rgb(53, 162, 235)',
          backgroundColor: 'rgba(53, 162, 235, 0.5)',
        });
      }
      return { datasets };
    }
    return { datasets: [] };
  };

  const staticBudget = {
    allocated: 5000000000,
    executed: 4850000000,
  };

  if (isLoading) {
    return <div className="step-container"><h2>Загрузка данных...</h2></div>;
  }

  if (!projectDetails) {
    return <div className="step-container"><p>Не удалось загрузить данные для выбранных параметров.</p></div>;
  }

  return (
    <div className="information-container">
      <div className="info-header-selectors">
        <RegionSelector
          regions={regions}
          selectedRegion={selectedRegion}
          onRegionSelect={onRegionSelect}
        />
        <GoalSelector
          goals={goals}
          selectedGoal={selectedGoal}
          onGoalSelect={onGoalSelect}
        />
        <ProjectSelector
          projects={projects}
          selectedProject={selectedProject}
          onProjectSelect={onProjectSelect}
        />
        <YearSelector
          selectedYear={selectedYear}
          onYearChange={onYearChange}
          availableYears={availableYears}
        />
      </div>

      {projectDetails && (
        <>
          <div className="info-details">
            <h3>Итоговая информация по проекту: {projectDetails.name}</h3>
          </div>

          {/* 3. Вставляем компонент таблицы бюджета */}
          <ProjectBudgetTable budget={staticBudget} />

          <IndicatorDisplay metrics={projectDetails.metrics} onShowChart={handleShowChart} />
          <MeasuresDisplay measures={projectDetails.activities} />
        </>
      )}

      {/* Модальное окно остается без изменений */}
      {modal.isOpen && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-graph" onClick={(e) => e.stopPropagation()}>
            <button onClick={handleCloseModal} className="close-graph-button">×</button>
            <div className="graph-header">
              <h5>Динамика: {modal.indicatorName}</h5>
            </div>
            {modal.isLoading ? (<p>Загрузка данных...</p>) : (
              <>
                <div className="chart-toggle-buttons">
                  <button onClick={() => setModal(prev => ({ ...prev, chartType: 'yearly' }))} className={modal.chartType === 'yearly' ? 'active' : ''} disabled={!modal.historyData?.yearly_data?.length} >По годам</button>
                  <button onClick={() => setModal(prev => ({ ...prev, chartType: 'monthly' }))} className={modal.chartType === 'monthly' ? 'active' : ''} disabled={!modal.historyData?.monthly_data?.length} >По месяцам</button>
                </div>
                <div className="chart-container"><LineChart chartData={getChartData()} title="" /></div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};


export default InformationDisplay;