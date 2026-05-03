import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { getProducts } from "../api/forecastApi";

export default function Controls({ onSubmit, loading }) {
  const { t } = useTranslation();
  const [products, setProducts] = useState([]);
  const [productQuery, setProductQuery] = useState("");
  const [storeId, setStoreId] = useState("");
  const [horizonDays, setHorizonDays] = useState(7);

  useEffect(() => {
    let cancelled = false;
    getProducts()
      .then((data) => {
        if (cancelled || !data?.length) return;
        setProducts(data);
        setProductQuery((prev) => {
          if (prev.trim()) return prev;
          return data[0].product_id;
        });
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  function submit(e) {
    e.preventDefault();
    onSubmit({
      productId: productQuery.trim(),
      storeId: storeId.trim() || null,
      horizonDays: Number(horizonDays),
    });
  }

  return (
    <form className="controls" onSubmit={submit}>
      <div className="field">
        <label>{t("controls.product")}</label>
        <input
          list="product-query-options"
          value={productQuery}
          onChange={(e) => setProductQuery(e.target.value)}
          placeholder={t("controls.productPlaceholder")}
          autoComplete="off"
        />
        <datalist id="product-query-options">
          {products.map((p) => (
            <option key={p.product_id} value={p.product_id}>
              {p.name || p.product_id}
            </option>
          ))}
        </datalist>
      </div>

      <div className="field">
        <label>{t("controls.storeId")}</label>
        <input value={storeId} onChange={(e) => setStoreId(e.target.value)} placeholder="S001" />
      </div>

      <div className="field">
        <label>{t("controls.horizonDays")}</label>
        <input
          type="number"
          min={1}
          max={30}
          value={horizonDays}
          onChange={(e) => setHorizonDays(e.target.value)}
        />
      </div>

      <button className="btn" disabled={loading}>
        {loading ? t("common.loading") : t("controls.getForecast")}
      </button>
    </form>
  );
}
