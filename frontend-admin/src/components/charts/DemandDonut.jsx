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
      },
    ],
  };

  const options = { responsive: true, maintainAspectRatio: false };

  return (
    <div className="chartBox">
      <Doughnut data={data} options={options} />
    </div>
  );
}
