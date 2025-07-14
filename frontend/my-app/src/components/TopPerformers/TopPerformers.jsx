import React from 'react';
import styles from './TopPerformers.module.css';

// Иконки для визуализации
const ArrowUp = () => <span className={`${styles.arrow} ${styles.up}`}>▲</span>;
const ArrowDown = () => <span className={`${styles.arrow} ${styles.down}`}>▼</span>;

const TopPerformers = ({ metrics }) => {
  // --- Логика для определения лучших и худших показателей ---
  // ПРИМЕЧАНИЕ: Сейчас используется мок-логика. В будущем это нужно будет получать с бэкенда.

  const allIndicators = metrics.flatMap(m => m.indicators);

  // Фильтруем только те, у которых есть значение и сравнение с РФ
  const validIndicators = allIndicators.filter(i =>
    typeof i.region_value === 'number' && typeof i.rf_value === 'number'
  );

  // Сортируем по дельте относительно РФ
  validIndicators.sort((a, b) => {
    const deltaA = a.region_value - a.rf_value;
    const deltaB = b.region_value - b.rf_value;

    // Если для показателя "чем ниже, тем лучше", инвертируем сортировку
    if (a.is_reversed) {
      return deltaA - deltaB; // Лучший тот, у кого дельта меньше (более отрицательная)
    }
    return deltaB - deltaA; // Лучший тот, у кого дельта больше
  });

  const bestIndicators = validIndicators.slice(0, 3);
  const worstIndicators = validIndicators.slice(-3).reverse();

  return (
    <div className={styles.performersContainer}>
      <h4>Ключевые показатели</h4>
      <div className={styles.columns}>
        <div className={styles.column}>
          <h5 className={styles.columnTitle}><ArrowUp /> Зоны роста</h5>
          <ul>
            {bestIndicators.map(ind => (
              <li key={ind.id}>{ind.name}</li>
            ))}
          </ul>
        </div>
        <div className={styles.column}>
          <h5 className={styles.columnTitle}><ArrowDown /> Точки внимания</h5>
          <ul>
            {worstIndicators.map(ind => (
              <li key={ind.id}>{ind.name}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default TopPerformers;
