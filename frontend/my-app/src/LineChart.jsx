import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  TimeSeriesScale,
} from 'chart.js';
import 'chartjs-adapter-date-fns'; // Важно для корректной работы временной оси

ChartJS.register(
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  TimeSeriesScale
);

const LineChart = ({ chartData, title }) => {
  // Проверка на случай, если данные некорректны
  if (!chartData || !chartData.datasets) {
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
        display: !!title,
        text: title,
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      },
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'year', // По умолчанию показываем года
          tooltipFormat: 'dd.MM.yyyy',
          displayFormats: {
            month: 'MMM yyyy',
            year: 'yyyy'
          },
        },
        title: {
          display: true,
          text: 'Дата'
        }
      },
      y: {
        title: {
          display: true,
          text: 'Значение'
        }
      }
    }
  };

  return <Line options={options} data={chartData} />;
};

export default LineChart;
