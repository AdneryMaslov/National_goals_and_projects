import React from 'react';

const formatDelta = (number) => {
  if (typeof number !== 'number' || isNaN(number)) {
    return null;
  }
  const rounded = Math.round(number * 100) / 100;
  return rounded > 0 ? `+${rounded}` : rounded;
};

const IndicatorDataCells = ({ indicator, onShowChart }) => {
  const deltaRf = (typeof indicator.region_value === 'number' && typeof indicator.rf_value === 'number')
    ? indicator.region_value - indicator.rf_value
    : null;

  const targetValueNumeric = parseFloat(String(indicator.target_value).replace(',', '.'));
  const deltaTarget = (typeof indicator.region_value === 'number' && !isNaN(targetValueNumeric))
    ? indicator.region_value - targetValueNumeric
    : null;

  const deltaRfIsGood = indicator.is_reversed ? deltaRf < 0 : deltaRf > 0;
  const deltaTargetIsGood = indicator.is_reversed ? deltaTarget <= 0 : deltaTarget >= 0;

  return (
    <>
      <td>{indicator.name || 'Название не найдено'}</td>
      <td className="text-bold">{indicator.region_value ?? null}</td>
      <td>{indicator.rf_value ? indicator.rf_value.toFixed(2) : null}</td>
      <td>{indicator.target_value ?? null}</td>
      <td className={deltaRf === null ? '' : (deltaRfIsGood ? 'text-green' : 'text-red')}>{formatDelta(deltaRf)}</td>
      <td className={deltaTarget === null ? '' : (deltaTargetIsGood ? 'text-green' : 'text-red')}>{formatDelta(deltaTarget)}</td>
      <td>
        <button className="chart-button" onClick={() => onShowChart(indicator.id, indicator.name)}>
          График
        </button>
      </td>
    </>
  );
};

const IndicatorDisplay = ({ metrics, onShowChart }) => {
  if (!metrics || metrics.length === 0) {
    return <p>Индикаторы для данного проекта не определены.</p>;
  }

  return (
    <div className="indicator-display">
      <h4>Индикаторы национальной цели</h4>
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
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((metric, metricIndex) => {
              const indicators = Array.isArray(metric.indicators) ? metric.indicators : [];
              if (indicators.length === 0) return null;

              const [firstIndicator, ...restIndicators] = indicators;

              return (
                <React.Fragment key={metric.name || metricIndex}>
                  <tr key={firstIndicator.name || 0}>
                    <td rowSpan={indicators.length} className="metric-name-cell">
                      {metric.name}
                    </td>
                    <IndicatorDataCells indicator={firstIndicator} onShowChart={onShowChart} />
                  </tr>
                  {restIndicators.map((indicator, indicatorIndex) => (
                    <tr key={indicator.name || indicatorIndex}>
                      <IndicatorDataCells indicator={indicator} onShowChart={onShowChart} />
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
