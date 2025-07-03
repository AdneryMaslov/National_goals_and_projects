import React from 'react';
import IndicatorDisplay from './IndicatorDisplay';
import MeasuresDisplay from './MeasuresDisplay';

const InformationDisplay = ({ regionName, goalName, project }) => {
  if (!project) {
    return (
       <div className="information-container">
         <p>Данные для этого выбора не найдены.</p>
      </div>
    );
  }

  return (
    <div className="information-container">
      <div className="info-header">
        <h3>Итоговая информация по проекту: {project.name}</h3>
        <p><strong>Регион:</strong> {regionName}</p>
        <p><strong>В рамках нац. цели:</strong> {goalName}</p>
      </div>
      
      <IndicatorDisplay indicators={project.indicators} />
      <MeasuresDisplay measures={project.measures} />
    </div>
  );
};

export default InformationDisplay;
