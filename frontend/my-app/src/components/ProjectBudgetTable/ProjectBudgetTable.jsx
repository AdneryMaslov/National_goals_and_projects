import React from 'react';
import styles from './ProjectBudgetTable.module.css';

// Вспомогательная функция для форматирования чисел
const formatCurrency = (number) => {
  if (typeof number !== 'number' || number === null) return 'N/A';
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(number);
};

// Компонент для одной строки таблицы
const BudgetRow = ({ item }) => {
  const executionPercentage = item.allocated > 0
    ? (item.executed / item.allocated * 100)
    : 0;

  return (
    <tr>
      <td>{item.name}</td>
      <td>{formatCurrency(item.allocated)}</td>
      <td>{formatCurrency(item.executed)}</td>
      <td className="text-bold">{executionPercentage.toFixed(1)}%</td>
    </tr>
  );
};

const ProjectBudgetTable = ({ budget, selectedRegion }) => {

  // --- НАЧАЛО ИЗМЕНЕНИЙ ---

  // Определяем, какие данные использовать: полученные с сервера или статические
  let displayBudget;
  let isStatic = false;

  if (!budget || budget.length === 0) {
    // Если данные с сервера не пришли, используем статические данные
    isStatic = true;
    displayBudget = [
        { name: "Российская Федерация", allocated: 15000000000, executed: 14800000000 },
        { name: selectedRegion?.name || "Выбранный регион", allocated: 5000000000, executed: 4850000000 }
    ];
  } else {
    // Иначе используем данные, пришедшие с сервера
    displayBudget = budget;
  }

  // --- КОНЕЦ ИЗМЕНЕНИЙ ---

  return (
    <div className={styles.budgetTableContainer}>
      <h4>Бюджет национального проекта {isStatic && "(пример данных)"}</h4>
      <div className="table-responsive">
        <table>
          <thead>
            <tr>
              <th>Уровень</th>
              <th>Бюджет выделено</th>
              <th>Бюджет исполнено</th>
              <th>Исполнено, %</th>
            </tr>
          </thead>
          <tbody>
            {displayBudget.map(item => (
              <BudgetRow key={item.name} item={item} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ProjectBudgetTable;