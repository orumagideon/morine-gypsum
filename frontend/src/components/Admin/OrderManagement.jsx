import React, { useEffect, useState } from "react";
import api from "../../api/axios";

export default function OrderManagement() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState(null);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await api.get("/orders/");
      setOrders(response.data);
    } catch (error) {
      console.error("Failed to fetch orders:", error);
      alert("Failed to load orders");
    } finally {
      setLoading(false);
    }
  };

  const updateOrderStatus = async (orderId, newStatus) => {
    try {
      await api.patch(`/orders/${orderId}`, { status: newStatus });
      alert("Order status updated successfully");
      fetchOrders();
      if (selectedOrder?.id === orderId) {
        setSelectedOrder({ ...selectedOrder, status: newStatus });
      }
    } catch (error) {
      console.error("Failed to update order status:", error);
      alert("Failed to update order status");
    }
  };

  const downloadInvoice = async (orderId) => {
    try {
      const response = await api.get(`/orders/${orderId}/invoice`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `invoice-${orderId}.pdf`);
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

  return (
    <div>
      <h2 className="mb-4">Order Management</h2>

      <div className="row">
        <div className={selectedOrder ? "col-md-7" : "col-md-12"}>
          <div className="table-responsive">
            <table className="table table-striped">
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Customer</th>
                  <th>Date</th>
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
                      {order.customer_name}
                      <br />
                      <small className="text-muted">{order.customer_phone}</small>
                    </td>
                    <td>
                      {new Date(order.created_at || order.order_date).toLocaleDateString()}
                    </td>
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
                      <button
                        className="btn btn-sm btn-info me-2"
                        onClick={() => setSelectedOrder(order)}
                      >
                        View
                      </button>
                      <button
                        className="btn btn-sm btn-success me-2"
                        onClick={() => downloadInvoice(order.id)}
                      >
                        Invoice
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {selectedOrder && (
          <div className="col-md-5">
            <div className="card">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h5>Order Details #{selectedOrder.id}</h5>
                <button
                  className="btn btn-sm btn-close"
                  onClick={() => setSelectedOrder(null)}
                ></button>
              </div>
              <div className="card-body">
                <div className="mb-3">
                  <strong>Customer:</strong> {selectedOrder.customer_name}
                  <br />
                  <strong>Phone:</strong> {selectedOrder.customer_phone}
                  <br />
                  <strong>Address:</strong> {selectedOrder.delivery_address}
                </div>

                <div className="mb-3">
                  <strong>Status:</strong>
                  <select
                    className="form-select mt-1"
                    value={selectedOrder.status || "pending"}
                    onChange={(e) =>
                      updateOrderStatus(selectedOrder.id, e.target.value)
                    }
                  >
                    <option value="pending">Pending</option>
                    <option value="processing">Processing</option>
                    <option value="shipped">Shipped</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>

                <div className="mb-3">
                  <strong>Order Items:</strong>
                  <ul className="list-group mt-2">
                    {selectedOrder.items?.map((item, idx) => (
                      <li key={idx} className="list-group-item">
                        {item.product?.name || `Product ID: ${item.product_id}`} - Qty:{" "}
                        {item.quantity} @ KES {item.price || item.product?.price}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="mb-3">
                  <strong>Total Amount:</strong> KES{" "}
                  {selectedOrder.total_amount?.toLocaleString() || "0"}
                </div>

                <div className="mb-3">
                  <strong>Order Date:</strong>{" "}
                  {new Date(
                    selectedOrder.created_at || selectedOrder.order_date
                  ).toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

