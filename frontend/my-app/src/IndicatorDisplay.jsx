import React from 'react';

// Вспомогательная функция для форматирования дельты
const formatDelta = (number) => {
  if (number === undefined || number === null) return 'N/A';
  const rounded = Math.round(number * 100) / 100;
  return rounded > 0 ? `+${rounded}` : rounded;
};

// Новый вспомогательный компонент для одной строки с данными индикатора
// Это делает основной компонент чище
const IndicatorDataCells = ({ indicator }) => {
  const deltaRf = indicator.regionValue - indicator.rfValue;
  const deltaTarget = indicator.regionValue - indicator.targetValue;
  const deltaRfIsGood = indicator.isReversed ? deltaRf < 0 : deltaRf > 0;
  const deltaTargetIsGood = indicator.isReversed ? deltaTarget <= 0 : deltaTarget >= 0;

  return (
    <>
      <td>{indicator.name}</td>
      <td className="text-bold">{indicator.regionValue}</td>
      <td>{indicator.rfValue}</td>
      <td>{indicator.targetValue}</td>
      <td className={deltaRfIsGood ? 'text-green' : 'text-red'}>{formatDelta(deltaRf)}</td>
      <td className={deltaTargetIsGood ? 'text-green' : 'text-red'}>{formatDelta(deltaTarget)}</td>
    </>
  );
};


const IndicatorDisplay = ({ metrics }) => {
  if (!metrics || metrics.length === 0) {
    return <p>Индикаторы для данного проекта не определены.</p>;
  }

  return (
    <div className="indicator-display">
      <h4>Индикаторы национального проекта</h4>
      <div className="table-responsive">
        <table>
          <thead>
            <tr>
              <th>Название показателя</th>
              <th>Название индикатора</th>
              <th>Значение</th>
              <th>Среднее РФ</th>
              <th>Цель</th>
              <th>Δ от РФ</th>
              <th>Δ от цели</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((metric) => {
              // Убедимся, что работаем с массивом
              const indicators = Array.isArray(metric.indicators) ? metric.indicators : [];
              // Явно отделяем первый индикатор от остальных
              const [firstIndicator, ...restIndicators] = indicators;

              return (
                <React.Fragment key={metric.name}>
                  {/* Рендерим первую строку, если она существует */}
                  {firstIndicator && (
                    <tr key={`${metric.name}-${firstIndicator.name}`}>
                      {/* Эта ячейка будет растянута на все строки своей группы */}
                      <td rowSpan={indicators.length} className="metric-name-cell">
                        {metric.name}
                      </td>
                      <IndicatorDataCells indicator={firstIndicator} />
                    </tr>
                  )}

                  {/* Рендерим остальные строки. В них нет первой ячейки. */}
                  {restIndicators.map((indicator) => (
                    <tr key={`${metric.name}-${indicator.name}`}>
                      <IndicatorDataCells indicator={indicator} />
                    </tr>
                  ))}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default IndicatorDisplay;
