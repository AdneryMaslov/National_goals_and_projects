import React from 'react';

// Функция для форматирования чисел в денежный формат
const formatCurrency = (number) => {
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', minimumFractionDigits: 0 }).format(number);
};

const BudgetDisplay = ({ budget }) => {
  if (!budget) return null;
  
  const executionPercentage = (budget.totalExecuted / budget.totalAllocated * 100).toFixed(1);

  return (
    <div className="budget-display">
       <h4>Бюджет</h4>
       <p>
         <strong>Всего назначено:</strong> {formatCurrency(budget.totalAllocated)}
       </p>
        <p>
         <strong>Всего исполнено:</strong> {formatCurrency(budget.totalExecuted)} ({executionPercentage}%)
       </p>
       {budget.projects && budget.projects.length > 0 && (
         <>
           <h5>В разрезе проектов:</h5>
           <ul>
             {budget.projects.map(p => (
                <li key={p.name}>
                  {p.name}: {formatCurrency(p.executed)} / {formatCurrency(p.allocated)}
                </li>
             ))}
           </ul>
         </>
       )}
    </div>
  );
};

export default BudgetDisplay;
