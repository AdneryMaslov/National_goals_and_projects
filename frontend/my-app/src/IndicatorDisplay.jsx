import React, { useState } from 'react';
import LineChart from './LineChart';

const IndicatorDisplay = ({ indicators }) => {
  // Вместо индекса будем хранить данные для активного графика
  const [activeChart, setActiveChart] = useState(null);

  // Функция для показа графика
  const showChart = (indicator) => {
    setActiveChart({
      data: indicator.chartData,
      title: `Динамика: ${indicator.name}`
    });
  };
  
  // Функция для скрытия графика
  const hideChart = () => {
    setActiveChart(null);
  };

  return (
    <div className="indicator-display">
      <h4>Ключевые показатели</h4>
      <div className="table-responsive">
        <table>
          <thead>
            <tr>
              <th>Показатель</th>
              <th>Среднее по РФ</th>
              <th>Показатель региона</th>
              <th>Действие</th>
            </tr>
          </thead>
          <tbody>
            {indicators.map((indicator) => {
              const isGood = indicator.isReversed
                ? indicator.regionValue < indicator.rfValue
                : indicator.regionValue > indicator.rfValue;
              
              const valueClass = isGood ? 'text-green' : 'text-red';

              return (
                <tr key={indicator.name}>
                  <td>{indicator.name}</td>
                  <td>{indicator.rfValue}</td>
                  <td className={valueClass}>{indicator.regionValue}</td>
                  <td>
                    <button onClick={() => showChart(indicator)}>
                      Показать график
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* --- График теперь отображается здесь, ВНЕ таблицы --- */}
      {activeChart && (
        <div className="graph-container modal-graph">
          <div className="graph-header">
             <h5>{activeChart.title}</h5>
             {/* Кнопка для скрытия графика теперь здесь */}
             <button onClick={hideChart} className="close-graph-button">Закрыть</button>
          </div>
          <LineChart chartData={activeChart.data} title={activeChart.title} />
        </div>
      )}
    </div>
  );
};

export default IndicatorDisplay;
