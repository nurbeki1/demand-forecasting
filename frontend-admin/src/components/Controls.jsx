import { useState } from "react";
import { useTranslation } from "react-i18next";

export default function Controls({ onSubmit, loading }) {
  const { t } = useTranslation();
  const [productId, setProductId] = useState("P0001");
  const [storeId, setStoreId] = useState(""); // optional
  const [horizonDays, setHorizonDays] = useState(7);

  function submit(e) {
    e.preventDefault();
    onSubmit({
      productId: productId.trim(),
      storeId: storeId.trim() || null,
      horizonDays: Number(horizonDays),
    });
  }

  return (
    <form className="controls" onSubmit={submit}>
      <div className="field">
        <label>{t('controls.productId')}</label>
        <input value={productId} onChange={(e) => setProductId(e.target.value)} placeholder="P0001" />
      </div>

      <div className="field">
        <label>{t('controls.storeId')}</label>
        <input value={storeId} onChange={(e) => setStoreId(e.target.value)} placeholder="S001" />
      </div>

      <div className="field">
        <label>{t('controls.horizonDays')}</label>
        <input
          type="number"
          min={1}
          max={30}
          value={horizonDays}
          onChange={(e) => setHorizonDays(e.target.value)}
        />
      </div>

      <button className="btn" disabled={loading}>
        {loading ? t('common.loading') : t('controls.getForecast')}
      </button>
    </form>
  );
}
