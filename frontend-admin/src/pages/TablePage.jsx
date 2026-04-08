import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import { getProducts, getHistory } from "../api/forecastApi";

export default function TablePage() {
  const { t } = useTranslation();
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [categories, setCategories] = useState([]);

  const [records, setRecords] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(false);

  const pageSize = 20;

  useEffect(() => {
    loadProducts();
  }, []);

  useEffect(() => {
    if (selectedProduct) {
      loadHistory();
    }
  }, [selectedProduct, page]);

  async function loadProducts() {
    try {
      const data = await getProducts();
      setProducts(data);

      // Extract unique categories
      const cats = [...new Set(data.map((p) => p.category).filter(Boolean))];
      setCategories(cats);

      if (data.length > 0) {
        setSelectedProduct(data[0].product_id);
      }
    } catch (err) {
      toast.error(t('common.error'));
    }
  }

  async function loadHistory() {
    setLoading(true);

    try {
      const data = await getHistory(selectedProduct, {
        limit: pageSize,
        offset: page * pageSize,
      });
      setRecords(data.records);
      setTotal(data.total);
    } catch (err) {
      toast.error(err.message || "Failed to load data");
    } finally {
      setLoading(false);
    }
  }

  const filteredProducts = selectedCategory
    ? products.filter((p) => p.category === selectedCategory)
    : products;

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="appShell">
      <Sidebar />
      <div className="main">
        <Topbar />
        <div className="content">
          <div className="headerRow">
            <div>
              <div className="title">{t('table.title')}</div>
              <div className="subtitle">{t('table.subtitle')}</div>
            </div>
          </div>

          <div className="panel">
            <div className="filterRow">
              <div className="field">
                <label>{t('common.category')}</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => {
                    setSelectedCategory(e.target.value);
                    setSelectedProduct("");
                    setRecords([]);
                  }}
                >
                  <option value="">{t('table.allCategories')}</option>
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>

              <div className="field">
                <label>{t('common.product')}</label>
                <select
                  value={selectedProduct}
                  onChange={(e) => {
                    setSelectedProduct(e.target.value);
                    setPage(0);
                  }}
                >
                  <option value="">{t('common.selectProduct')}</option>
                  {filteredProducts.map((p) => (
                    <option key={p.product_id} value={p.product_id}>
                      {p.product_id} ({p.total_records} {t('table.records')})
                    </option>
                  ))}
                </select>
              </div>
            </div>

          </div>

          <div className="card">
            <div className="cardHeader">
              <div>
                <div className="cardTitle">
                  {selectedProduct ? `${t('table.salesHistory')} - ${selectedProduct}` : t('table.salesHistory')}
                </div>
                {total > 0 && (
                  <div className="cardSub">
                    {t('table.showing')} {page * pageSize + 1}-{Math.min((page + 1) * pageSize, total)} {t('common.of')} {total} {t('table.records')}
                  </div>
                )}
              </div>
            </div>

            {loading ? (
              <div className="emptyBox">{t('common.loading')}</div>
            ) : records.length > 0 ? (
              <>
                <div className="tableWrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>{t('common.date')}</th>
                        <th>{t('table.unitsSold')}</th>
                        <th>{t('common.category')}</th>
                        <th>{t('table.region')}</th>
                        <th>{t('common.price')}</th>
                        <th>{t('table.inventory')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {records.map((row, idx) => (
                        <tr key={idx}>
                          <td>{row.date}</td>
                          <td>
                            <strong>{row.units_sold.toFixed(0)}</strong>
                          </td>
                          <td>{row.category || "-"}</td>
                          <td>{row.region || "-"}</td>
                          <td>${row.price.toFixed(2)}</td>
                          <td>{row.inventory_level.toFixed(0)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="pagination">
                  <button
                    onClick={() => setPage((p) => Math.max(0, p - 1))}
                    disabled={page === 0}
                  >
                    {t('common.previous')}
                  </button>
                  <span>
                    {t('common.page')} {page + 1} {t('common.of')} {totalPages}
                  </span>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                    disabled={page >= totalPages - 1}
                  >
                    {t('common.next')}
                  </button>
                </div>
              </>
            ) : (
              <div className="emptyBox">
                {selectedProduct
                  ? t('common.noData')
                  : t('common.selectProduct')}
              </div>
            )}
          </div>

          {products.length > 0 && (
            <div className="card" style={{ marginTop: 16 }}>
              <div className="cardHeader">
                <div className="cardTitle">{t('table.productsSummary')}</div>
              </div>
              <div className="tableWrap">
                <table className="table">
                  <thead>
                    <tr>
                      <th>{t('table.productId')}</th>
                      <th>{t('common.category')}</th>
                      <th>{t('table.totalRecords')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredProducts.slice(0, 10).map((p) => (
                      <tr
                        key={p.product_id}
                        onClick={() => {
                          setSelectedProduct(p.product_id);
                          setPage(0);
                        }}
                        style={{ cursor: "pointer" }}
                      >
                        <td>
                          <strong>{p.product_id}</strong>
                        </td>
                        <td>{p.category || "-"}</td>
                        <td>{p.total_records}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
