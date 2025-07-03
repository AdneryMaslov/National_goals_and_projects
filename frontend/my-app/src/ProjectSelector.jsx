import React from 'react';

const ProjectSelector = ({ projects, onProjectSelect }) => {
  const handleSelect = (e) => {
    const selectedProjectName = e.target.value;
    const selectedProjectObject = projects.find(p => p.name === selectedProjectName);
    onProjectSelect(selectedProjectObject);
  };

  return (
    <div>
      <select defaultValue="" onChange={handleSelect}>
        <option value="" disabled>-- Выберите нац. проект --</option>
        {projects.map(project => (
          <option key={project.name} value={project.name}>
            {project.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default ProjectSelector;
