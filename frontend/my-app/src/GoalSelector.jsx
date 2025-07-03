import React from 'react';

const GoalSelector = ({ goals, onGoalSelect }) => {
  const handleSelect = (e) => {
    const selectedGoalName = e.target.value;
    const selectedGoalObject = goals.find(g => g.name === selectedGoalName);
    onGoalSelect(selectedGoalObject);
  };

  return (
    <div>
      <select defaultValue="" onChange={handleSelect}>
        <option value="" disabled>-- Выберите нац. цель --</option>
        {goals.map(goal => (
          <option key={goal.name} value={goal.name}>
            {goal.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default GoalSelector;
