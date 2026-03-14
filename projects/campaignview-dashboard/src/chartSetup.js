import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
  Filler,
);

// Shared default options
export const defaultLineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        padding: 20,
        usePointStyle: true,
        pointStyleWidth: 10,
        font: { size: 12, family: 'Inter' },
      },
    },
    tooltip: {
      backgroundColor: '#1a1a2e',
      titleFont: { family: 'Inter', weight: '600' },
      bodyFont: { family: 'Inter' },
      padding: 12,
      cornerRadius: 8,
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { font: { size: 11, family: 'Inter' } },
    },
    y: {
      grid: { color: '#f0f1f5' },
      ticks: { font: { size: 11, family: 'Inter' } },
    },
  },
};

export const defaultBarOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#1a1a2e',
      titleFont: { family: 'Inter', weight: '600' },
      bodyFont: { family: 'Inter' },
      padding: 12,
      cornerRadius: 8,
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { font: { size: 11, family: 'Inter' } },
    },
    y: {
      grid: { color: '#f0f1f5' },
      ticks: { font: { size: 11, family: 'Inter' } },
    },
  },
};

export const defaultDoughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '65%',
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        padding: 20,
        usePointStyle: true,
        pointStyleWidth: 10,
        font: { size: 12, family: 'Inter' },
      },
    },
    tooltip: {
      backgroundColor: '#1a1a2e',
      titleFont: { family: 'Inter', weight: '600' },
      bodyFont: { family: 'Inter' },
      padding: 12,
      cornerRadius: 8,
    },
  },
};
