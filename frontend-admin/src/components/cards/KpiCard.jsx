export default function KpiCards({ productId, storeId, horizonDays, total, avg, lastDate }) {
  return (
    <div className="kpiRow">
      <div className="kpiCard">
        <div className="kpiLabel">Product</div>
        <div className="kpiValue">{productId}</div>
      </div>

      <div className="kpiCard">
        <div className="kpiLabel">Store</div>
        <div className="kpiValue">{storeId || "All"}</div>
      </div>

      <div className="kpiCard">
        <div className="kpiLabel">Horizon</div>
        <div className="kpiValue">{horizonDays} days</div>
      </div>

      <div className="kpiCard">
        <div className="kpiLabel">Avg predicted</div>
        <div className="kpiValue">{avg.toFixed(2)}</div>
      </div>

      <div className="kpiCard">
        <div className="kpiLabel">Total predicted</div>
        <div className="kpiValue">{total.toFixed(2)}</div>
      </div>

      <div className="kpiCard">
        <div className="kpiLabel">Last history date</div>
        <div className="kpiValue">{lastDate}</div>
      </div>
    </div>
  );
}
