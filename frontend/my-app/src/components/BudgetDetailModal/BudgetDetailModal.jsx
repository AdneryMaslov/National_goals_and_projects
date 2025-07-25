import React, { useState } from 'react';
import LineChart from '../InformationDisplay/LineChart/LineChart';
import BarChart from '../InformationDisplay/BarChart/BarChart'; // <-- Импортируем BarChart
import styles from './BudgetDetailModal.module.css';

// Вспомогательные компоненты и функции (formatCurrency, BudgetDataTable)
const formatCurrency = (number) => { if (typeof number !== 'number' || number === null) return 'N/A'; const fullAmount = number * 1000000; return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(fullAmount); };
const BudgetDataTable = ({ title, data }) => ( <div className={styles.tableSection}> <h5>{title}</h5> <div className={styles.tableWrapper}> <table> <thead className={styles.stickyHeader}> <tr> <th style={{ fontWeight: 'bold', color: 'black' }}>Месяц</th> <th style={{ fontWeight: 'bold', color: 'black' }}>Выделено</th> <th style={{ fontWeight: 'bold', color: 'black' }}>Исполнено</th> <th style={{ fontWeight: 'bold', color: 'black' }}>%</th> </tr> </thead> <tbody> {data.map(item => { const percentage = item.amount_allocated > 0 ? (item.amount_executed / item.amount_allocated * 100) : 0; return ( <tr key={item.relevance_date}> <td>{new Date(item.relevance_date).toLocaleString('ru-RU', { month: 'long' })}</td> <td>{formatCurrency(item.amount_allocated)}</td> <td>{formatCurrency(item.amount_executed)}</td> <td>{percentage.toFixed(1)}%</td> </tr> ) })} </tbody> </table> </div> </div> );

const BudgetDetailModal = ({ isOpen, onClose, data, isLoading, projectName, regionName, year }) => {
    const [chartView, setChartView] = useState({ region: 'absolute', rf: 'absolute' });
    const getAbsoluteRegionChartData = () => { if (!data?.region_data?.length) return { datasets: [] }; return { datasets: [ { label: `Исполнено (${regionName})`, data: data.region_data.map(d => ({ x: new Date(d.relevance_date), y: d.amount_executed })), borderColor: 'rgb(255, 99, 132)', backgroundColor: 'rgba(255, 99, 132, 0.5)', tension: 0.1, }, { label: `Назначено (${regionName})`, data: data.region_data.map(d => ({ x: new Date(d.relevance_date), y: d.amount_allocated })), borderColor: 'rgb(75, 192, 192)', backgroundColor: 'rgba(75, 192, 192, 0.5)', borderDash: [5, 5], tension: 0.1, } ] }; };
    const getAbsoluteRfChartData = () => { if (!data?.rf_data?.length) return { datasets: [] }; return { datasets: [ { label: 'Исполнено (РФ)', data: data.rf_data.map(d => ({ x: new Date(d.relevance_date), y: d.amount_executed })), borderColor: 'rgb(53, 162, 235)', backgroundColor: 'rgba(53, 162, 235, 0.5)', tension: 0.1, }, { label: 'Назначено (РФ)', data: data.rf_data.map(d => ({ x: new Date(d.relevance_date), y: d.amount_allocated })), borderColor: 'rgb(255, 159, 64)', backgroundColor: 'rgba(255, 159, 64, 0.5)', borderDash: [5, 5], tension: 0.1, } ] }; };

    // Функции для подготовки данных для Bar Chart
    const getPercentageRegionChartData = () => {
        if (!data?.region_data?.length) return { labels: [], datasets: [] };
        const labels = data.region_data.map(d => new Date(d.relevance_date).toLocaleString('ru-RU', { month: 'long' }));
        const chartData = data.region_data.map(d => {
            const perc = d.amount_allocated > 0 ? (d.amount_executed / d.amount_allocated * 100) : 0;
            return perc.toFixed(2);
        });
        return {
            labels,
            datasets: [{ label: `Исполнение, % (${regionName})`, data: chartData, backgroundColor: 'rgba(153, 102, 255, 0.7)' }]
        };
    };
    const getPercentageRfChartData = () => {
        if (!data?.rf_data?.length) return { labels: [], datasets: [] };
        const labels = data.rf_data.map(d => new Date(d.relevance_date).toLocaleString('ru-RU', { month: 'long' }));
        const chartData = data.rf_data.map(d => {
            const perc = d.amount_allocated > 0 ? (d.amount_executed / d.amount_allocated * 100) : 0;
            return perc.toFixed(2);
        });
        return {
            labels,
            datasets: [{ label: 'Исполнение, % (РФ)', data: chartData, backgroundColor: 'rgba(255, 206, 86, 0.7)' }]
        };
    };

    const hasRegionData = data?.region_data?.length > 0;
    const hasRfData = data?.rf_data?.length > 0;
    const isRfSelected = regionName === 'Российская Федерация';

    return (
        <div className={styles.modalOverlay} onClick={onClose}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                <button onClick={onClose} className={styles.closeButton}>×</button>
                <div className={styles.header}>
                    <h3>Детализация бюджета: {projectName} ({year} г.)</h3>
                </div>
                {isLoading ? ( <p>Загрузка данных...</p> ) : !hasRegionData && !hasRfData ? ( <p>Нет помесячных данных для отображения.</p> ) : (
                    isRfSelected ? (
                        <div className={styles.singleColumnContainer}>
                            {hasRfData ? (
                                <>
                                    <BudgetDataTable title="Российская Федерация" data={data.rf_data} />
                                    <div className={styles.chartSection}>
                                        <div className={styles.chartToggle}>
                                            <button onClick={() => setChartView(p => ({...p, rf: 'absolute'}))} className={chartView.rf === 'absolute' ? styles.active : ''}>В рублях</button>
                                            <button onClick={() => setChartView(p => ({...p, rf: 'percentage'}))} className={chartView.rf === 'percentage' ? styles.active : ''}>В процентах</button>
                                        </div>
                                        <div className={styles.chartContainer}>
                                            {chartView.rf === 'absolute' ? (
                                                <LineChart chartData={getAbsoluteRfChartData()} chartType="monthly" yAxisTitle={'Значение, млн руб'} />
                                            ) : (
                                                <BarChart chartData={getPercentageRfChartData()} yAxisTitle={'Исполнение, %'} />
                                            )}
                                        </div>
                                    </div>
                                </>
                            ) : <p>Нет данных по РФ</p>}
                        </div>
                    ) : (
                        <div className={styles.comparisonContainer}>
                            {hasRegionData ? <BudgetDataTable title={regionName} data={data.region_data} /> : <div/>}
                            {hasRfData ? <BudgetDataTable title="Российская Федерация" data={data.rf_data} /> : <div/>}
                            {hasRegionData ? (
                                <div className={styles.chartSection}>
                                    <div className={styles.chartToggle}>
                                        <button onClick={() => setChartView(p => ({...p, region: 'absolute'}))} className={chartView.region === 'absolute' ? styles.active : ''}>В рублях</button>
                                        <button onClick={() => setChartView(p => ({...p, region: 'percentage'}))} className={chartView.region === 'percentage' ? styles.active : ''}>В процентах</button>
                                    </div>
                                    <div className={styles.chartContainer}>
                                        {chartView.region === 'absolute' ? (
                                            <LineChart chartData={getAbsoluteRegionChartData()} chartType="monthly" yAxisTitle={'Значение, млн руб'} />
                                        ) : (
                                            <BarChart chartData={getPercentageRegionChartData()} yAxisTitle={'Исполнение, %'} />
                                        )}
                                    </div>
                                </div>
                            ) : <div/>}
                            {hasRfData ? (
                                <div className={styles.chartSection}>
                                    <div className={styles.chartToggle}>
                                        <button onClick={() => setChartView(p => ({...p, rf: 'absolute'}))} className={chartView.rf === 'absolute' ? styles.active : ''}>В рублях</button>
                                        <button onClick={() => setChartView(p => ({...p, rf: 'percentage'}))} className={chartView.rf === 'percentage' ? styles.active : ''}>В процентах</button>
                                    </div>
                                    <div className={styles.chartContainer}>
                                        {chartView.rf === 'absolute' ? (
                                            <LineChart chartData={getAbsoluteRfChartData()} chartType="monthly" yAxisTitle={'Значение, млн руб'} />
                                        ) : (
                                            <BarChart chartData={getPercentageRfChartData()} yAxisTitle={'Исполнение, %'} />
                                        )}
                                    </div>
                                </div>
                            ) : <div/>}
                        </div>
                    )
                )}
            </div>
        </div>
    );
};

export default BudgetDetailModal;