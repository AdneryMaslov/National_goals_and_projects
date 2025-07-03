import React, { useState } from 'react';
import LineChart from './LineChart';

// --- Вспомогательные функции для форматирования ---

// Форматирует числа в денежный формат (1000 -> 1 000 ₽)
const formatCurrency = (number) => {
  if (number === undefined || number === null) return 'N/A';
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', minimumFractionDigits: 0 }).format(number);
};

// Форматирует дельту, добавляя знак "+" и округляя до 2 знаков
const formatDelta = (number) => {
  if (number === undefined || number === null) return 'N/A';
  const rounded = Math.round(number * 100) / 100;
  return rounded > 0 ? `+${rounded}` : rounded;
};

const IndicatorDisplay = ({ indicators }) => {
  const [activeChart, setActiveChart] = useState(null);

  const showChart = (indicator) => {
    setActiveChart({
      data: indicator.chartData,
      title: `Динамика: ${indicator.name}`
    });
  };
  
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
              <th>Название показателя</th>
              <th>Значение</th>
              <th>Среднее РФ</th>
              <th>Цель</th>
              <th>Δ от РФ</th>
              <th>Δ от цели</th>
              <th>Бюджет, выдел.</th>
              <th>Бюджет, исполн.</th>
              <th>Исполн., %</th>
              <th>График</th>
            </tr>
          </thead>
          <tbody>
            {indicators.map((indicator) => {
              // --- Расчеты ---
              const deltaRf = indicator.regionValue - indicator.rfValue;
              const deltaTarget = indicator.regionValue - indicator.targetValue;
              const budgetPercentage = indicator.budget.allocated > 0 
                ? (indicator.budget.executed / indicator.budget.allocated * 100)
                : 0;

              // --- Логика для подсветки ---
              // isReversed = true (бедность): хорошо, когда дельта отрицательная
              // isReversed = false (ОПЖ): хорошо, когда дельта положительная
              const deltaRfIsGood = indicator.isReversed ? deltaRf < 0 : deltaRf > 0;
              const deltaTargetIsGood = indicator.isReversed ? deltaTarget <= 0 : deltaTarget >= 0;

              return (
                <tr key={indicator.name}>
                  <td>{indicator.name}</td>
                  <td className="text-bold">{indicator.regionValue}</td>
                  <td>{indicator.rfValue}</td>
                  <td>{indicator.targetValue}</td>
                  <td className={deltaRfIsGood ? 'text-green' : 'text-red'}>{formatDelta(deltaRf)}</td>
                  <td className={deltaTargetIsGood ? 'text-green' : 'text-red'}>{formatDelta(deltaTarget)}</td>
                  <td>{formatCurrency(indicator.budget.allocated)}</td>
                  <td>{formatCurrency(indicator.budget.executed)}</td>
                  <td className="text-bold">{budgetPercentage.toFixed(1)}%</td>
                  <td>
                    <button onClick={() => showChart(indicator)} title="Показать график динамики">
                      📈
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {activeChart && (
        <div className="graph-container modal-graph">
          <div className="graph-header">
             <h5>{activeChart.title}</h5>
             <button onClick={hideChart} className="close-graph-button">Закрыть</button>
          </div>
          <LineChart chartData={activeChart.data} title={activeChart.title} />
        </div>
      )}
    </div>
  );
};

export default IndicatorDisplay;
