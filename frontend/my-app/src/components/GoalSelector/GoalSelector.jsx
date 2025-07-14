import React from 'react';
import styles from './GoalSelector.module.css';

const GoalSelector = ({ goals, selectedGoal, onGoalSelect }) => {
  const handleSelect = (e) => {
    const selectedGoalId = e.target.value;
    const selectedGoalObject = goals.find(g => g.id === parseInt(selectedGoalId));
    onGoalSelect(selectedGoalObject);
  };

  return (
    <div className={styles.selectorWrapper}>
      <label className={styles.label} htmlFor="goal-select">Нац. цель:</label>
      <select
        id="goal-select"
        className={styles.selectElement}
        value={selectedGoal?.id || ''}
        onChange={handleSelect}
      >
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
