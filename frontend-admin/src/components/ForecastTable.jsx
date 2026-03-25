export default function ForecastTable({ predictions }) {
  return (
    <div className="tableWrap">
      <table className="table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Predicted Units Sold</th>
          </tr>
        </thead>
        <tbody>
          {predictions.map((p) => (
            <tr key={p.date}>
              <td>{p.date}</td>
              <td>{Number(p.predicted_units_sold).toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
