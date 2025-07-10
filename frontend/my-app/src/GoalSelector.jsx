import React from 'react';

const GoalSelector = ({ goals, selectedGoal, onGoalSelect }) => {
  const handleSelect = (e) => {
    const selectedGoalId = e.target.value;
    const selectedGoalObject = goals.find(g => g.id === parseInt(selectedGoalId));
    onGoalSelect(selectedGoalObject);
  };

  return (
    <div className="selector-wrapper">
      <label>Нац. цель:</label>
      <select value={selectedGoal?.id || ''} onChange={handleSelect}>
        <option value="" disabled>-- Выберите нац. цель --</option>
        {goals.map(goal => (
          <option key={goal.id} value={goal.id}>
            {goal.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default GoalSelector;