import React, { useEffect, useState } from "react";
import api from "../api/axios";
import { Link } from "react-router-dom";

export default function ProductList({ categoryId, searchTerm }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProducts();
  }, [categoryId, searchTerm]);

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

  if (loading) {
    return (
      <div className="d-flex justify-content-center p-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="alert alert-info">
        <p>No products found. Try adjusting your filters.</p>
      </div>
    );
  }

  return (
    <div className="row">
      {products.map((p) => (
        <div key={p.id} className="col-md-4 mb-4">
          <div className="card h-100">
            {p.image_url && (
              <img
                src={
                  p.image_url.startsWith("http")
                    ? p.image_url
                    : `${api.defaults.baseURL}${p.image_url}`
                }
                className="card-img-top"
                alt={p.name}
                style={{ height: 200, objectFit: "cover" }}
              />
            )}
            <div className="card-body d-flex flex-column">
              <h5 className="card-title">{p.name}</h5>
              {p.category && (
                <span className="badge bg-secondary mb-2">{p.category.name}</span>
              )}
              <p className="card-text flex-grow-1">
                {p.description?.substring(0, 100)}
                {p.description?.length > 100 ? "..." : ""}
              </p>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <strong className="text-primary">KES {p.price?.toLocaleString()}</strong>
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
                <Link
                  to={`/products/${p.id}`}
                  className="btn btn-primary"
                >
                  View Details
                </Link>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
