import React, { useState } from 'react';

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
        <div className="measures-display">
            <h4>Мероприятия национального проекта в регионе</h4>
            <ul>
                {measures.map((measure, index) => (
                    <li key={index}>
                        <span className="measure-date">
                            {measure.activity_date ? new Date(measure.activity_date).toLocaleDateString('ru-RU') : 'Нет даты'}
                        </span>
                        {/* При клике на заголовок открываем модальное окно */}
                        <button className="measure-title-button" onClick={() => openModal(measure)}>
                            {measure.title}
                        </button>
                    </li>
                ))}
            </ul>

            {/* Модальное окно */}
            {selectedNews && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h3>{selectedNews.title}</h3>
                        <p className="modal-text">{selectedNews.text}</p>
                        <div className="modal-actions">
                            {selectedNews.link && (
                                <a href={selectedNews.link} target="_blank" rel="noopener noreferrer" className="measure-link">
                                    Подробнее
                                </a>
                            )}
                            <button onClick={closeModal} className="modal-close-button">
                                Закрыть
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MeasuresDisplay;