import React from 'react';

// Вспомогательная функция для форматирования чисел в денежный формат
const formatCurrency = (number) => {
  if (number === undefined || number === null) return 'N/A';
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', minimumFractionDigits: 0 }).format(number);
};

const ProjectBudgetTable = ({ budget }) => {
  if (!budget) return null;

  const executionPercentage = budget.allocated > 0
    ? (budget.executed / budget.allocated * 100)
    : 0;

  return (
    <div className="budget-table-container">
      <h4>Бюджет национального проекта</h4>
      <div className="table-responsive">
        <table>
          <thead>
            <tr>
              <th>Бюджет выделено</th>
              <th>Бюджет исполнено</th>
              <th>Исполнено, %</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{formatCurrency(budget.allocated)}</td>
              <td>{formatCurrency(budget.executed)}</td>
              <td className="text-bold">{executionPercentage.toFixed(1)}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ProjectBudgetTable;
