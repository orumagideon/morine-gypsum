import React, { useState, useEffect } from "react";
import api from "../../api/axios";

export default function ProductForm({ product, categories = [], onSuccess, onCancel }) {
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const [price, setPrice] = useState("");
  const [stock, setStock] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (product) {
      setName(product.name || "");
      setDesc(product.description || "");
      setPrice(product.price || "");
      setStock(product.stock_quantity || "");
      setCategoryId(product.category_id || product.category?.id || "");
    }
  }, [product]);

  async function submit(e) {
    e.preventDefault();
    setLoading(true);

    const fd = new FormData();
    fd.append("name", name);
    fd.append("description", desc || "");
    fd.append("price", price);
    fd.append("stock_quantity", stock);
    // Always append category_id, even if empty (to allow clearing category on update)
    if (product) {
      fd.append("category_id", categoryId || "");
    } else {
      if (categoryId && categoryId !== "") {
        fd.append("category_id", categoryId);
      }
    }
    if (file) {
      fd.append("image", file);
    }

    try {
      if (product) {
        // Update existing product
        await api.put(`/products/${product.id}`, fd, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        alert("Product updated successfully!");
      } else {
        // Create new product
        await api.post("/products/", fd, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        alert("Product created successfully!");
      }
      if (onSuccess) onSuccess();
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Failed to save product");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={submit}>
      <h4>{product ? "Edit Product" : "Add New Product"}</h4>
      <div className="row">
        <div className="col-md-6 mb-3">
          <label className="form-label">Product Name *</label>
          <input
            className="form-control"
            placeholder="Product Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div className="col-md-6 mb-3">
          <label className="form-label">Category</label>
          <select
            className="form-select"
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
          >
            <option value="">Select Category</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="mb-3">
        <label className="form-label">Description *</label>
        <textarea
          className="form-control"
          placeholder="Product Description"
          value={desc}
          onChange={(e) => setDesc(e.target.value)}
          rows="3"
          required
        />
      </div>
      <div className="row">
        <div className="col-md-6 mb-3">
          <label className="form-label">Price (KES) *</label>
          <input
            type="number"
            step="0.01"
            min="0"
            className="form-control"
            placeholder="Price"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            required
          />
        </div>
        <div className="col-md-6 mb-3">
          <label className="form-label">Stock Quantity *</label>
          <input
            type="number"
            min="0"
            className="form-control"
            placeholder="Stock Quantity"
            value={stock}
            onChange={(e) => setStock(e.target.value)}
            required
          />
        </div>
      </div>
      <div className="mb-3">
        <label className="form-label">Product Image</label>
        <input
          type="file"
          className="form-control"
          accept="image/*"
          onChange={(e) => setFile(e.target.files[0])}
        />
        {product?.image_url && !file && (
          <small className="text-muted">
            Current image: {product.image_url}
          </small>
        )}
      </div>
      <div className="d-flex gap-2">
        <button
          className="btn btn-primary"
          type="submit"
          disabled={loading}
        >
          {loading ? "Saving..." : product ? "Update" : "Create"}
        </button>
        {onCancel && (
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCancel}
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
