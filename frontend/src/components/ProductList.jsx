import React, { useContext, useEffect, useState } from "react";
import api from "../api/axios";
import { Link } from "react-router-dom";
import { CartContext } from "../context/CartContext";

export default function ProductList({ categoryId, searchTerm }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState(() => {
    const savedView = localStorage.getItem("productViewMode");
    if (savedView === "grid" || savedView === "list") {
      return savedView;
    }
    return window.matchMedia("(max-width: 768px)").matches ? "grid" : "list";
  });
  const { addToCart } = useContext(CartContext);

  const changeViewMode = (mode) => {
    setViewMode(mode);
    localStorage.setItem("productViewMode", mode);
  };
  const viewToggle = (
    <div className="product-feed-toolbar" role="group" aria-label="Product display options">
      <span className="product-feed-label">View products</span>
      <button
        type="button"
        className={`btn btn-sm ${viewMode === "grid" ? "btn-primary" : "btn-outline-primary"}`}
        aria-pressed={viewMode === "grid"}
        onClick={() => changeViewMode("grid")}
      >
        Grid
      </button>
      <button
        type="button"
        className={`btn btn-sm ${viewMode === "list" ? "btn-primary" : "btn-outline-primary"}`}
        aria-pressed={viewMode === "list"}
        onClick={() => changeViewMode("list")}
      >
        List
      </button>
    </div>
  );

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      try {
        let url = "/products/";
        const params = new URLSearchParams();
        if (categoryId) {
          params.append("category_id", categoryId);
        }
        if (searchTerm) {
          params.append("search", searchTerm);
        }
        if (params.toString()) {
          url += `?${params.toString()}`;
        }

        const response = await api.get(url);
        setProducts(response.data);
      } catch (err) {
        console.error(err);
        alert("Failed to load products");
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [categoryId, searchTerm]);

  if (loading) {
    return (
      <>
        {viewToggle}
        <div className="d-flex justify-content-center p-5">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </>
    );
  }

  if (products.length === 0) {
    return (
      <>
        {viewToggle}
        <div className="alert alert-info">
          <p>No products found. Try adjusting your filters.</p>
        </div>
      </>
    );
  }

  return (
    <>
      {viewToggle}
      <div className={`product-grid product-grid--${viewMode}`}>
        {products.map((p) => {
          const isOutOfStock =
            p.stock_quantity !== undefined && Number(p.stock_quantity) <= 0;

          return (
            <article key={p.id} className="product-card card h-100">
              {p.image_url ? (
                <img
                  src={
                    p.image_url.startsWith("http")
                      ? p.image_url
                      : `${api.defaults.baseURL}${p.image_url}`
                  }
                  className="card-img-top"
                  loading="lazy"
                  alt={p.name}
                />
              ) : (
                <div className="product-image-placeholder" aria-hidden="true" />
              )}
              <div className="card-body d-flex flex-column">
                <h5 className="card-title">
                  <Link to={`/products/${p.id}`} className="product-title-link">
                    {p.name}
                  </Link>
                </h5>
                {p.category && (
                  <span className="badge bg-secondary mb-2">{p.category.name}</span>
                )}
                <p className="card-text product-description flex-grow-1">
                  {p.description?.substring(0, 120)}
                  {p.description?.length > 120 ? "..." : ""}
                </p>
                <div className="product-card-footer">
                  <div>
                    <strong className="text-primary product-price">
                      KES {p.price?.toLocaleString()}
                    </strong>
                    {p.stock_quantity !== undefined && (
                      <div>
                        <small
                          className={
                            p.stock_quantity < 10 ? "text-danger" : "text-muted"
                          }
                        >
                          {p.stock_quantity > 0
                            ? `${p.stock_quantity} in stock`
                            : "Out of stock"}
                        </small>
                      </div>
                    )}
                  </div>
                  <div className="product-card-actions">
                    <button
                      type="button"
                      className="btn btn-primary btn-sm"
                      onClick={() => addToCart(p)}
                      disabled={isOutOfStock}
                    >
                      {isOutOfStock ? "Out of Stock" : "Add to Cart"}
                    </button>
                    <Link
                      to={`/products/${p.id}`}
                      className="btn btn-outline-secondary btn-sm"
                    >
                      Details
                    </Link>
                  </div>
                </div>
              </div>
            </article>
          );
        })}
      </div>
    </>
  );
}
