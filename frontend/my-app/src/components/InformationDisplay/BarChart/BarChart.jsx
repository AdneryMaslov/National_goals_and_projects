import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const BarChart = ({ chartData, yAxisTitle = 'Значение' }) => {
  if (!chartData || !chartData.datasets || chartData.datasets.length === 0) {
    return <p>Нет данных для отображения графика.</p>;
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: false,
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Месяц'
        }
      },
      y: {
        title: {
          display: true,
          text: yAxisTitle
        },
        // Добавляем знак '%' к значениям на оси Y
        ticks: {
          callback: function(value) {
            return value + '%';
          }
        },
        max: 100, // Устанавливаем максимум оси Y на 100%
        beginAtZero: true
      }
    }
  };

  return <Bar options={options} data={chartData} />;
};

export default BarChart;