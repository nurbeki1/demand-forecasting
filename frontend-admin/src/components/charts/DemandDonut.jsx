import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function DemandDonut({ buckets }) {
  const data = {
    labels: ["Q1", "Q2", "Q3", "Q4"],
    datasets: [
      {
        label: "Demand structure",
        data: buckets,
        backgroundColor: [
          "rgba(0, 229, 255, 0.8)",
          "rgba(0, 255, 136, 0.8)",
          "rgba(168, 85, 247, 0.8)",
          "rgba(255, 170, 0, 0.8)",
        ],
        borderColor: [
          "#00e5ff",
          "#00ff88",
          "#a855f7",
          "#ffaa00",
        ],
        borderWidth: 2,
        hoverBackgroundColor: [
          "#00e5ff",
          "#00ff88",
          "#a855f7",
          "#ffaa00",
        ],
        hoverBorderColor: "#ffffff",
        hoverBorderWidth: 3,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: "bottom",
        labels: {
          color: "#4a6580",
          font: {
            family: "'Space Mono', monospace",
            size: 11,
          },
          padding: 16,
          usePointStyle: true,
          pointStyle: "circle",
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
    cutout: "65%",
  };

  return (
    <div className="chartBox">
      <Doughnut data={data} options={options} />
    </div>
  );
}