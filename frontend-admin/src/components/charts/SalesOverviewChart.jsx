import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

export default function SalesOverviewChart({ predictions }) {
  const labels = predictions.map((p) => p.date);
  const values = predictions.map((p) => p.predicted_units_sold);

  const data = {
    labels,
    datasets: [
      {
        label: "Predicted Units Sold",
        data: values,
        tension: 0.35,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: true } },
  };

  return (
    <div className="chartBox">
      <Line data={data} options={options} />
    </div>
  );
}
