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
import 'chartjs-adapter-date-fns';
import { ru } from 'date-fns/locale';

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

const LineChart = ({ chartData, title, chartType }) => {
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
        adapters: {
            date: {
                locale: ru,
            },
        },
        time: {
          unit: chartType === 'yearly' ? 'year' : 'month',
          tooltipFormat: 'd MMMM yyyy',
          displayFormats: {
            month: "MMM ''yy",
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
