import React, { useState } from 'react';
import styles from './MeasuresDisplay.module.css';

const MeasuresDisplay = ({ measures }) => {
    const [selectedNews, setSelectedNews] = useState(null);

    const openModal = (newsItem) => {
        setSelectedNews(newsItem);
    };

    const closeModal = () => {
        setSelectedNews(null);
    };

    if (!measures || measures.length === 0) {
        return <p>Для данного проекта и региона не найдено актуальных мероприятий.</p>;
    }

    return (
        <div className={styles.measuresDisplay}>
            <h4>Мероприятия национального проекта в регионе</h4>
            <ul>
                {measures.map((measure, index) => (
                    <li key={measure.link || index} className={styles.measureItem} onClick={() => openModal(measure)}>
                        <span className={styles.date}>
                            {measure.activity_date ? new Date(measure.activity_date).toLocaleDateString('ru-RU') : ''}
                        </span>
                        <p className={styles.title}>
                            {measure.title}
                        </p>
                    </li>
                ))}
            </ul>

            {selectedNews && (
                <div className={styles.modalOverlay} onClick={closeModal}>
                    <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                        {/* 1. Добавлена кнопка-крестик */}
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
