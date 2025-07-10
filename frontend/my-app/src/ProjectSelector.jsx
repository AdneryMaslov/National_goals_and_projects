import React from 'react';

const ProjectSelector = ({ projects, selectedProject, onProjectSelect }) => {
  const handleSelect = (e) => {
    const selectedProjectId = e.target.value;
    const selectedProjectObject = projects.find(p => p.id === parseInt(selectedProjectId));
    onProjectSelect(selectedProjectObject);
  };

  return (
    <div className="selector-wrapper">
      <label>Нац. проект:</label>
      <select value={selectedProject?.id || ''} onChange={handleSelect}>
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