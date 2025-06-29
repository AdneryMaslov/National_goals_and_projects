import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend
);

// Компонент теперь принимает данные и заголовок через пропсы
const LineChart = ({ chartData, title }) => {
  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: title, // Используем переданный заголовок
      },
    },
  };
  
  // Добавляем стили к данным
  const styledChartData = {
    ...chartData,
    datasets: chartData.datasets.map((ds, index) => ({
      ...ds,
      borderColor: index === 0 ? 'rgb(255, 99, 132)' : 'rgb(53, 162, 235)',
      backgroundColor: index === 0 ? 'rgba(255, 99, 132, 0.5)' : 'rgba(53, 162, 235, 0.5)',
    }))
  };

  return <Line options={options} data={styledChartData} />;
};

export default LineChart;
