import React, { useState, useEffect, useRef } from 'react';
import styles from './SearchableSelector.module.css';

const SearchableSelector = ({ options, value, onChange, label, placeholder }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const wrapperRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const filteredOptions = options.filter(option =>
    option.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSelect = (option) => {
    onChange(option);
    setSearchTerm('');
    setIsOpen(false);
  };

  const handleInputChange = (e) => {
    setSearchTerm(e.target.value);
    if (!isOpen) {
      setIsOpen(true);
    }
  }

  return (
    <div className={styles.selectorWrapper} ref={wrapperRef}>
      <label className={styles.label}>{label}</label>
      <div className={styles.inputContainer}>
        {/* ИЗМЕНЕНИЕ: Добавляем класс hasValue, если значение выбрано */}
        <input
          type="text"
          className={`${styles.input} ${value ? styles.hasValue : ''}`}
          placeholder={value ? value.name : placeholder}
          value={searchTerm}
          onChange={handleInputChange}
          onFocus={() => setIsOpen(true)}
        />
        <span className={styles.arrow}>{isOpen ? '▲' : '▼'}</span>
      </div>
      {isOpen && (
        <ul className={styles.optionsList}>
          {filteredOptions.length > 0 ? (
            filteredOptions.map(option => (
              <li
                key={option.id}
                className={styles.optionItem}
                onClick={() => handleSelect(option)}
              >
                {option.name}
              </li>
            ))
          ) : (
            <li className={styles.noOptions}>Ничего не найдено</li>
          )}
        </ul>
      )}
    </div>
  );
};

export default SearchableSelector;
