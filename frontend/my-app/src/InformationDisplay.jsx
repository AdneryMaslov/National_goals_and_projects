import React from 'react';
import IndicatorDisplay from './IndicatorDisplay';
import BudgetDisplay from './BudgetDisplay';
import MeasuresDisplay from './MeasuresDisplay';

const InformationDisplay = ({ region, selection, data }) => {
  // Показываем сообщение, если по какой-то причине данных нет
  if (!data) {
    return (
       <div className="information-container">
         <p>Данные для этого выбора не найдены.</p>
      </div>
    );
  }

  return (
    <div className="information-container">
      <div className="info-header">
        <h3>Итоговая информация</h3>
        <p><strong>Регион:</strong> {region}</p>
        <p><strong>{selection.type === 'goal' ? 'Нац. цель' : 'Нац. проект'}:</strong> {selection.value}</p>
      </div>
      
      {/* Передаем конкретные части данных в дочерние компоненты */}
      <IndicatorDisplay indicators={data.indicators} />
      <BudgetDisplay budget={data.budget} />
      <MeasuresDisplay measures={data.measures} />
    </div>
  );
};

export default InformationDisplay;
