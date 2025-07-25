import React, { useState, useMemo } from 'react';
import styles from './MeasuresDisplay.module.css';

// Вспомогательная функция для определения цвета значка важности
const getImportanceColor = (level) => {
    if (level >= 8) return styles.highImportance;
    if (level >= 5) return styles.mediumImportance;
    return styles.lowImportance;
};

const MeasuresDisplay = ({ measures }) => {
    const [selectedNews, setSelectedNews] = useState(null);
    // --- ИЗМЕНЕНИЕ ЗДЕСЬ: Одно состояние для управления обоими фильтрами ---
    const [sortConfig, setSortConfig] = useState('date_desc'); // e.g., 'date_desc', 'importance_asc'

    const openModal = (newsItem) => {
        setSelectedNews(newsItem);
    };

    const closeModal = () => {
        setSelectedNews(null);
    };

    // Мемоизация отсортированного списка новостей
    const sortedMeasures = useMemo(() => {
        if (!measures) return [];
        const sorted = [...measures];

        const [sortBy, sortDirection] = sortConfig.split('_');

        sorted.sort((a, b) => {
            if (sortBy === 'importance') {
                const valA = a.importance ?? -1;
                const valB = b.importance ?? -1;
                return sortDirection === 'desc' ? valB - valA : valA - valB;
            } else { // sortBy === 'date'
                const dateA = a.activity_date ? new Date(a.activity_date).getTime() : 0;
                const dateB = b.activity_date ? new Date(b.activity_date).getTime() : 0;
                return sortDirection === 'desc' ? dateB - dateA : dateA - dateB;
            }
        });
        return sorted;
    }, [measures, sortConfig]);


    if (!measures || measures.length === 0) {
        return (
            <div className={styles.measuresDisplay}>
                <h4>Мероприятия национального проекта в регионе</h4>
                <p>Для данного проекта и региона не найдено актуальных мероприятий.</p>
            </div>
        );
    }

    return (
        <div className={styles.measuresDisplay}>
            {/* --- ИЗМЕНЕНИЕ ЗДЕСЬ: Два независимых фильтра --- */}
            <div className={styles.header}>
                <h4>Мероприятия национального проекта в регионе</h4>
                <div className={styles.sortContainer}>
                    {/* Фильтр по дате */}
                    <select
                        value={sortConfig.startsWith('date') ? sortConfig : 'default_date'}
                        onChange={(e) => setSortConfig(e.target.value)}
                        className={styles.sortSelect}
                    >
                        <option value="default_date" disabled>По новизне</option>
                        <option value="date_desc">Сначала новые</option>
                        <option value="date_asc">Сначала старые</option>
                    </select>

                    {/* Фильтр по важности */}
                    <select
                        value={sortConfig.startsWith('importance') ? sortConfig : 'default_importance'}
                        onChange={(e) => setSortConfig(e.target.value)}
                        className={styles.sortSelect}
                    >
                        <option value="default_importance" disabled>По важности</option>
                        <option value="importance_desc">Сначала важные</option>
                        <option value="importance_asc">Сначала неважные</option>
                    </select>
                </div>
            </div>

            <ul>
                {sortedMeasures.map((measure) => (
                    <li key={measure.link || measure.title} className={styles.measureItem} onClick={() => openModal(measure)}>
                        <div className={styles.dateAndImportance}>
                            <span className={styles.date}>
                                {measure.activity_date ? new Date(measure.activity_date).toLocaleDateString('ru-RU') : ''}
                            </span>
                            {measure.importance != null && (
                                <span className={`${styles.importanceBadge} ${getImportanceColor(measure.importance)}`}>
                                    Важность: {measure.importance}
                                </span>
                            )}
                        </div>
                        <p className={styles.title}>
                            {measure.title}
                        </p>
                    </li>
                ))}
            </ul>

            {selectedNews && (
                <div className={styles.modalOverlay} onClick={closeModal}>
                    <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                        <button onClick={closeModal} className={styles.closeButton}>×</button>
                        <h3>{selectedNews.title}</h3>
                        <p className={styles.modalText}>{selectedNews.text}</p>
                        <div className={styles.modalActions}>
                            {selectedNews.link && (
                                <a href={selectedNews.link} target="_blank" rel="noopener noreferrer" className={styles.detailsLink}>
                                    Перейти к источнику
                                </a>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MeasuresDisplay;
