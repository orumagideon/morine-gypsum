import React, { useEffect, useState } from "react";
import ProductList from "../components/ProductList";
import api from "../api/axios";

function Store() {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await api.get("/categories/");
      setCategories(response.data);
    } catch (error) {
      console.error("Failed to fetch categories:", error);
    }
  };

  return (
    <div className="container mt-4">
      <div className="row mb-4">
        <div className="col-md-12">
          <h1>Our Store</h1>
          <p>Browse our available gypsum products below.</p>
        </div>
      </div>

      <div className="row mb-4">
        <div className="col-md-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Filter Products</h5>
              <div className="mb-3">
                <label className="form-label">Search</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search products..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Category</label>
                <select
                  className="form-select"
                  value={selectedCategory || ""}
                  onChange={(e) =>
                    setSelectedCategory(e.target.value || null)
                  }
                >
                  <option value="">All Categories</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>
              <button
                className="btn btn-secondary w-100"
                onClick={() => {
                  setSelectedCategory(null);
                  setSearchTerm("");
                }}
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>
        <div className="col-md-8">
          <ProductList
            categoryId={selectedCategory}
            searchTerm={searchTerm}
          />
        </div>
      </div>
    </div>
  );
}

export default Store;
