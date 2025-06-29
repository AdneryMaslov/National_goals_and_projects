import React, { useState } from 'react';

// Компонент теперь получает списки доступных целей и проектов
const GoalProjectSelector = ({ availableGoals, availableProjects, onGoalOrProjectSelect }) => {
  const [selectionType, setSelectionType] = useState('goal');

  const handleSelect = (value) => {
    onGoalOrProjectSelect({ type: selectionType, value: value });
  };

  return (
    <div className="goal-project-selector">
      <div>
        <label>
          <input
            type="radio"
            value="goal"
            checked={selectionType === 'goal'}
            onChange={e => setSelectionType(e.target.value)}
          />
          Национальная цель
        </label>
        <label>
          <input
            type="radio"
            value="project"
            checked={selectionType === 'project'}
            onChange={e => setSelectionType(e.target.value)}
          />
          Национальный проект
        </label>
      </div>

      {selectionType === 'goal' && (
        <select defaultValue="" onChange={e => handleSelect(e.target.value)}>
          <option value="" disabled>-- Выберите нац. цель --</option>
          {availableGoals.map(goal => <option key={goal} value={goal}>{goal}</option>)}
        </select>
      )}

      {selectionType === 'project' && (
        <select defaultValue="" onChange={e => handleSelect(e.target.value)}>
          <option value="" disabled>-- Выберите нац. проект --</option>
          {availableProjects.map(project => <option key={project} value={project}>{project}</option>)}
        </select>
      )}
    </div>
  );
};

export default GoalProjectSelector;
