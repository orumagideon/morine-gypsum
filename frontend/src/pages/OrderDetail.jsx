import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import api from "../api/axios";

export default function OrderDetail() {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchOrder();
  }, [id]);

  const fetchOrder = async () => {
    try {
      const response = await api.get(`/orders/${id}`);
      setOrder(response.data);
    } catch (error) {
      console.error("Failed to fetch order:", error);
      alert("Order not found");
      navigate("/store");
    } finally {
      setLoading(false);
    }
  };

  const downloadInvoice = async () => {
    try {
      const response = await api.get(`/orders/${id}/invoice`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `invoice-${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Failed to download invoice:", error);
      alert("Failed to download invoice");
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

  if (!order) {
    return (
      <div className="container mt-5">
        <div className="alert alert-danger">Order not found</div>
        <Link to="/store" className="btn btn-primary">
          Back to Store
        </Link>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Order Confirmation #{order.id}</h2>
        <button className="btn btn-primary" onClick={downloadInvoice}>
          Download Invoice
        </button>
      </div>

      <div className="row">
        <div className="col-md-8">
          <div className="card mb-3">
            <div className="card-header">
              <h5>Order Details</h5>
            </div>
            <div className="card-body">
              <p>
                <strong>Order Date:</strong>{" "}
                {new Date(order.created_at || order.order_date).toLocaleString()}
              </p>
              <p>
                <strong>Status:</strong>{" "}
                <span
                  className={`badge ${
                    order.status === "completed"
                      ? "bg-success"
                      : order.status === "pending"
                      ? "bg-warning"
                      : order.status === "cancelled"
                      ? "bg-danger"
                      : "bg-info"
                  }`}
                >
                  {order.status || "pending"}
                </span>
              </p>
            </div>
          </div>

          <div className="card mb-3">
            <div className="card-header">
              <h5>Customer Information</h5>
            </div>
            <div className="card-body">
              <p>
                <strong>Name:</strong> {order.customer_name}
              </p>
              <p>
                <strong>Phone:</strong> {order.customer_phone}
              </p>
              {order.customer_email && (
                <p>
                  <strong>Email:</strong> {order.customer_email}
                </p>
              )}
              <p>
                <strong>Delivery Address:</strong> {order.delivery_address}
              </p>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h5>Order Items</h5>
            </div>
            <div className="card-body">
              <table className="table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {order.items?.map((item, idx) => (
                    <tr key={idx}>
                      <td>{item.product?.name || `Product ID: ${item.product_id}`}</td>
                      <td>{item.quantity}</td>
                      <td>KES {item.price || item.product?.price}</td>
                      <td>
                        KES{" "}
                        {(
                          (item.price || item.product?.price) * item.quantity
                        ).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card">
            <div className="card-body">
              <h5>Order Summary</h5>
              <div className="d-flex justify-content-between mb-2">
                <span>Subtotal:</span>
                <span>KES {order.subtotal?.toLocaleString() || "0"}</span>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span>Shipping:</span>
                <span>KES {order.shipping_cost?.toLocaleString() || "500"}</span>
              </div>
              <hr />
              <div className="d-flex justify-content-between">
                <strong>Total:</strong>
                <strong>
                  KES {order.total_amount?.toLocaleString() || "0"}
                </strong>
              </div>
              {order.payment_method && (
                <div className="mt-3">
                  <strong>Payment Method:</strong>{" "}
                  {order.payment_method.replace("_", " ").toUpperCase()}
                </div>
              )}
            </div>
          </div>

          <div className="mt-3">
            <Link to="/store" className="btn btn-primary w-100">
              Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

