import React, { useEffect, useState, useContext } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function AdminDashboard() {
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalOrders: 0,
    totalRevenue: 0,
    lowStockItems: 0,
  });
  const [loading, setLoading] = useState(true);
  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const [productsRes, ordersRes] = await Promise.all([
        api.get("/products/"),
        api.get("/orders/"),
      ]);

      const products = productsRes.data;
      const orders = ordersRes.data;

      const totalRevenue = orders.reduce(
        (sum, order) => sum + (order.total_amount || 0),
        0
      );
      const lowStockItems = products.filter(
        (p) => p.stock_quantity < 10
      ).length;

      setStats({
        totalProducts: products.length,
        totalOrders: orders.length,
        totalRevenue,
        lowStockItems,
      });
    } catch (error) {
      console.error("Failed to fetch stats:", error);
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
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Admin Dashboard</h2>
        <div>
          <button
            className="btn btn-outline-secondary me-2"
            onClick={() => {
              if (confirm("Log out?")) {
                logout();
                // After logout, send user to home page
                navigate("/");
              }
            }}
          >
            Logout
          </button>
        </div>
      </div>

      <div className="row mb-4">
        <div className="col-md-3 mb-3">
          <div className="card bg-primary text-white">
            <div className="card-body">
              <h5 className="card-title">Total Products</h5>
              <h2>{stats.totalProducts}</h2>
            </div>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card bg-success text-white">
            <div className="card-body">
              <h5 className="card-title">Total Orders</h5>
              <h2>{stats.totalOrders}</h2>
            </div>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card bg-info text-white">
            <div className="card-body">
              <h5 className="card-title">Total Revenue</h5>
              <h2>KES {stats.totalRevenue.toLocaleString()}</h2>
            </div>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card bg-warning text-white">
            <div className="card-body">
              <h5 className="card-title">Low Stock Items</h5>
              <h2>{stats.lowStockItems}</h2>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-md-6 mb-3">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Quick Actions</h5>
              <div className="d-grid gap-2">
                <Link to="/admin/products" className="btn btn-primary">
                  Manage Products
                </Link>
                <Link to="/admin/categories" className="btn btn-secondary">
                  Manage Categories
                </Link>
                <Link to="/admin/orders" className="btn btn-success">
                  View Orders
                </Link>
                <Link to="/admin/settings" className="btn btn-info">
                  System Settings
                </Link>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-6 mb-3">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">System Information</h5>
              <p>
                <strong>Role:</strong> Admin
              </p>
              <p>
                <strong>Status:</strong> Active
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

