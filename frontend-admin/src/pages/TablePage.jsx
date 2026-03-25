import { useState, useEffect } from "react";
import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import { getProducts, getHistory } from "../api/forecastApi";

export default function TablePage() {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [categories, setCategories] = useState([]);

  const [records, setRecords] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

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
      setError("Failed to load products");
    }
  }

  async function loadHistory() {
    setLoading(true);
    setError("");

    try {
      const data = await getHistory(selectedProduct, {
        limit: pageSize,
        offset: page * pageSize,
      });
      setRecords(data.records);
      setTotal(data.total);
    } catch (err) {
      setError(err.message || "Failed to load data");
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
              <div className="title">Data Table</div>
              <div className="subtitle">Browse historical sales data</div>
            </div>
          </div>

          <div className="panel">
            <div className="filterRow">
              <div className="field">
                <label>Category</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => {
                    setSelectedCategory(e.target.value);
                    setSelectedProduct("");
                    setRecords([]);
                  }}
                >
                  <option value="">All Categories</option>
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>

              <div className="field">
                <label>Product</label>
                <select
                  value={selectedProduct}
                  onChange={(e) => {
                    setSelectedProduct(e.target.value);
                    setPage(0);
                  }}
                >
                  <option value="">Select Product</option>
                  {filteredProducts.map((p) => (
                    <option key={p.product_id} value={p.product_id}>
                      {p.product_id} ({p.total_records} records)
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {error && <div className="errorBox">{error}</div>}
          </div>

          <div className="card">
            <div className="cardHeader">
              <div>
                <div className="cardTitle">
                  {selectedProduct ? `Sales History - ${selectedProduct}` : "Sales History"}
                </div>
                {total > 0 && (
                  <div className="cardSub">
                    Showing {page * pageSize + 1}-{Math.min((page + 1) * pageSize, total)} of {total} records
                  </div>
                )}
              </div>
            </div>

            {loading ? (
              <div className="emptyBox">Loading...</div>
            ) : records.length > 0 ? (
              <>
                <div className="tableWrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Units Sold</th>
                        <th>Category</th>
                        <th>Region</th>
                        <th>Price</th>
                        <th>Inventory</th>
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
                    Previous
                  </button>
                  <span>
                    Page {page + 1} of {totalPages}
                  </span>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                    disabled={page >= totalPages - 1}
                  >
                    Next
                  </button>
                </div>
              </>
            ) : (
              <div className="emptyBox">
                {selectedProduct
                  ? "No data available"
                  : "Select a product to view data"}
              </div>
            )}
          </div>

          {products.length > 0 && (
            <div className="card" style={{ marginTop: 16 }}>
              <div className="cardHeader">
                <div className="cardTitle">Products Summary</div>
              </div>
              <div className="tableWrap">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Product ID</th>
                      <th>Category</th>
                      <th>Total Records</th>
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
