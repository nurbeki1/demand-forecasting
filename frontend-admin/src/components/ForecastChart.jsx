import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement
} from "chart.js";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement);

export default function ForecastChart({ data }) {
  if (!data || !data.forecast || !data.dates) return null;

  return (
    <Line
      data={{
        labels: data.dates,
        datasets: [
          {
            label: "Demand forecast",
            data: data.forecast,
            borderColor: "#4f46e5",
            backgroundColor: "#4f46e5",
          }
        ]
      }}
    />
  );
}
