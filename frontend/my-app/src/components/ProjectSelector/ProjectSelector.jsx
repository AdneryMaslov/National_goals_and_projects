import React from 'react';
import styles from './ProjectSelector.module.css';

const ProjectSelector = ({ projects, selectedProject, onProjectSelect }) => {
  const handleSelect = (e) => {
    const selectedProjectId = e.target.value;
    const selectedProjectObject = projects.find(p => p.id === parseInt(selectedProjectId));
    onProjectSelect(selectedProjectObject);
  };

  return (
    <div className={styles.selectorWrapper}>
      <label className={styles.label} htmlFor="project-select">Нац. проект:</label>
      <select
        id="project-select"
        className={styles.selectElement}
        value={selectedProject?.id || ''}
        onChange={handleSelect}
      >
        <option value="" disabled>-- Выберите нац. проект --</option>
        {projects.map(project => (
          <option key={project.id} value={project.id}>
            {project.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default ProjectSelector;
