import React, { useEffect, useState, useContext } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api/axios";
import { CartContext } from "../context/CartContext";

export default function ProductDetail() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const { addToCart } = useContext(CartContext);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await api.get(`/products/${id}`);
        setProduct(response.data);
      } catch (error) {
        console.error("Failed to fetch product:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [id]);

  if (loading) return <div>Loading...</div>;
  if (!product) return <div>Product not found</div>;

  return (
    <div style={{ textAlign: "center", marginTop: "20px" }}>
      <h3>{product.name}</h3>

      {product.image_url && (
        <img
          src={
            product.image_url.startsWith("http")
              ? product.image_url
              : `${api.defaults.baseURL}${product.image_url}`
          }
          alt={product.name}
          style={{ maxWidth: 300, borderRadius: 10 }}
        />
      )}

      <p>{product.description}</p>
      <p>
        <strong>Price:</strong> KES {product.price}
      </p>
      <p>
        <strong>Stock:</strong> {product.stock_quantity}
      </p>

      <button
        onClick={() => {
          addToCart(product, 1);
          navigate("/cart");
        }}
        style={{
          backgroundColor: "#28a745",
          color: "white",
          padding: "10px 20px",
          border: "none",
          borderRadius: "8px",
          cursor: "pointer",
        }}
      >
        Add to Cart
      </button>
    </div>
  );
}
