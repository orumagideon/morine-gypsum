import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";

export default function OrderHistory() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      // This endpoint should return orders for the current customer
      // For now, we'll use the general orders endpoint
      // In production, you'd filter by customer email/phone
      const response = await api.get("/orders/");
      setOrders(response.data);
    } catch (error) {
      console.error("Failed to fetch orders:", error);
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

  return (
    <div className="container mt-4">
      <h2 className="mb-4">Order History</h2>

      {orders.length === 0 ? (
        <div className="alert alert-info">
          <p>You haven't placed any orders yet.</p>
          <Link to="/store" className="btn btn-primary">
            Start Shopping
          </Link>
        </div>
      ) : (
        <div className="table-responsive">
          <table className="table table-striped">
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Date</th>
                <th>Items</th>
                <th>Total</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.id}>
                  <td>#{order.id}</td>
                  <td>
                    {new Date(
                      order.created_at || order.order_date
                    ).toLocaleDateString()}
                  </td>
                  <td>{order.items?.length || 0} item(s)</td>
                  <td>KES {order.total_amount?.toLocaleString() || "0"}</td>
                  <td>
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
                  </td>
                  <td>
                    <Link
                      to={`/orders/${order.id}`}
                      className="btn btn-sm btn-primary"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

