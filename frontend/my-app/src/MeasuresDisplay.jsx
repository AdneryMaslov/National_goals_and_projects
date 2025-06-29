import React from 'react';

const MeasuresDisplay = ({ measures }) => {
    if (!measures || measures.length === 0) return null;

    return (
        <div className="measures-display">
            <h4>Основные мероприятия по достижению показателей</h4>
            <ul>
                {measures.map((measure, index) => (
                    <li key={index}>{measure}</li>
                ))}
            </ul>
        </div>
    );
};

export default MeasuresDisplay;
