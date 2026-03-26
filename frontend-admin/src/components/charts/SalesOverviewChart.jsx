import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler);

export default function SalesOverviewChart({ predictions }) {
  const labels = predictions.map((p) => p.date);
  const values = predictions.map((p) => p.predicted_units_sold);

  const data = {
    labels,
    datasets: [
      {
        label: "Predicted Units Sold",
        data: values,
        tension: 0.4,
        borderColor: "#00e5ff",
        backgroundColor: "rgba(0, 229, 255, 0.1)",
        fill: true,
        pointBackgroundColor: "#00e5ff",
        pointBorderColor: "#00e5ff",
        pointHoverBackgroundColor: "#00ff88",
        pointHoverBorderColor: "#00ff88",
        pointRadius: 4,
        pointHoverRadius: 6,
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        labels: {
          color: "#4a6580",
          font: {
            family: "'Space Mono', monospace",
            size: 11,
          },
        },
      },
      tooltip: {
        backgroundColor: "rgba(5, 13, 26, 0.95)",
        titleColor: "#00e5ff",
        bodyColor: "#e8f4fc",
        borderColor: "rgba(0, 229, 255, 0.3)",
        borderWidth: 1,
        titleFont: {
          family: "'Space Mono', monospace",
        },
        bodyFont: {
          family: "'Space Mono', monospace",
        },
        padding: 12,
        cornerRadius: 8,
      },
    },
    scales: {
      x: {
        grid: {
          color: "rgba(0, 229, 255, 0.08)",
        },
        ticks: {
          color: "#4a6580",
          font: {
            family: "'Space Mono', monospace",
            size: 10,
          },
        },
      },
      y: {
        grid: {
          color: "rgba(0, 229, 255, 0.08)",
        },
        ticks: {
          color: "#4a6580",
          font: {
            family: "'Space Mono', monospace",
            size: 10,
          },
        },
      },
    },
  };

  return (
    <div className="chartBox">
      <Line data={data} options={options} />
    </div>
  );
}