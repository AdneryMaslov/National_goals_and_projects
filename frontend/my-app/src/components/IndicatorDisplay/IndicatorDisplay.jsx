import React, { useState } from 'react';
import styles from './IndicatorDisplay.module.css';

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
      <td className={styles.unitCell}>{indicator.unit || '-'}</td>
      <td className="text-bold">{indicator.region_value ?? null}</td>
      <td>{indicator.rf_value ? indicator.rf_value.toFixed(2) : null}</td>
      <td>{indicator.target_value ?? null}</td>
      <td className={deltaRf === null ? '' : (deltaRfIsGood ? 'text-green' : 'text-red')}>{formatDelta(deltaRf)}</td>
      <td className={deltaTarget === null ? '' : (deltaTargetIsGood ? 'text-green' : 'text-red')}>{formatDelta(deltaTarget)}</td>
      <td>
        <button className={styles.chartButton} onClick={() => onShowChart(indicator.id, indicator.name)}>
          График
        </button>
      </td>
    </>
  );
};

const IndicatorDisplay = ({ metrics, onShowChart }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!metrics || metrics.length === 0) {
    return <p>Индикаторы для данного проекта не определены.</p>;
  }

  return (
    <div className={styles.indicatorDisplay}>
      <div className={styles.header}>
        <h4>Все показатели и их индикаторы Наццели</h4>
      </div>

      {/* Кнопка "Свернуть" появляется сверху, только когда таблица развернута */}
      {isExpanded && (
        <div className={styles.collapseButtonWrapper} onClick={() => setIsExpanded(false)}>
          <span className={styles.toggleButton}>Свернуть таблицу</span>
        </div>
      )}

      <div className={`${styles.tableWrapper} ${!isExpanded ? styles.collapsed : ''}`}>
        <div className="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Название показателя</th>
                <th>Название индикатора</th>
                <th className={styles.unitCell}>Ед. изм.</th>
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
                    <tr key={firstIndicator.id || 0}>
                      <td rowSpan={indicators.length} className={styles.metricNameCell}>
                        {metric.name}
                      </td>
                      <IndicatorDataCells indicator={firstIndicator} onShowChart={onShowChart} />
                    </tr>
                    {restIndicators.map((indicator, indicatorIndex) => (
                      <tr key={indicator.id || indicatorIndex}>
                        <IndicatorDataCells indicator={indicator} onShowChart={onShowChart} />
                      </tr>
                    ))}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Кнопка "Развернуть" появляется снизу, только когда таблица свернута */}
        {!isExpanded && (
          <div className={styles.showMoreOverlay} onClick={() => setIsExpanded(true)}>
            <span className={styles.showMoreText}>Развернуть всю таблицу</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default IndicatorDisplay;