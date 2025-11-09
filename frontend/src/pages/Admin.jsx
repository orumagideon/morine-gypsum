import React from "react";
import { Routes, Route, Link, useLocation } from "react-router-dom";
import AdminDashboard from "./AdminDashboard";
import AdminLogin from "./AdminLogin";
import ProtectedRoute from "../components/ProtectedRoute";
import ProductManagement from "../components/Admin/ProductManagement";
import CategoryManagement from "../components/Admin/CategoryManagement";
import OrderManagement from "../components/Admin/OrderManagement";
import Settings from "../components/Admin/Settings";

function Admin() {
  const location = useLocation();

  return (
    <div className="container-fluid">
        <nav className="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
          <div className="container-fluid">
            <Link className="navbar-brand" to="/admin/dashboard">
              Admin Panel
            </Link>
            <button
              className="navbar-toggler"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#adminNav"
            >
              <span className="navbar-toggler-icon"></span>
            </button>
            <div className="collapse navbar-collapse" id="adminNav">
              <ul className="navbar-nav me-auto">
                <li className="nav-item">
                  <Link
                    className={`nav-link ${
                      location.pathname === "/admin/dashboard" ? "active" : ""
                    }`}
                    to="/admin/dashboard"
                  >
                    Dashboard
                  </Link>
                </li>
                <li className="nav-item">
                  <Link
                    className={`nav-link ${
                      location.pathname === "/admin/products" ? "active" : ""
                    }`}
                    to="/admin/products"
                  >
                    Products
                  </Link>
                </li>
                <li className="nav-item">
                  <Link
                    className={`nav-link ${
                      location.pathname === "/admin/categories" ? "active" : ""
                    }`}
                    to="/admin/categories"
                  >
                    Categories
                  </Link>
                </li>
                <li className="nav-item">
                  <Link
                    className={`nav-link ${
                      location.pathname === "/admin/orders" ? "active" : ""
                    }`}
                    to="/admin/orders"
                  >
                    Orders
                  </Link>
                </li>
                <li className="nav-item">
                  <Link
                    className={`nav-link ${
                      location.pathname === "/admin/settings" ? "active" : ""
                    }`}
                    to="/admin/settings"
                  >
                    Settings
                  </Link>
                </li>
              </ul>
            </div>
          </div>
        </nav>

        <div className="container-fluid">
          <Routes>
            {/* Public login route for admins */}
            <Route path="login" element={<AdminLogin />} />

            {/* Protected admin routes - require authentication */}
            <Route
              path="dashboard"
              element={
                <ProtectedRoute requireAdmin>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="products"
              element={
                <ProtectedRoute requireAdmin>
                  <ProductManagement />
                </ProtectedRoute>
              }
            />
            <Route
              path="categories"
              element={
                <ProtectedRoute requireAdmin>
                  <CategoryManagement />
                </ProtectedRoute>
              }
            />
            <Route
              path="orders"
              element={
                <ProtectedRoute requireAdmin>
                  <OrderManagement />
                </ProtectedRoute>
              }
            />
            <Route
              path="settings"
              element={
                <ProtectedRoute requireAdmin>
                  <Settings />
                </ProtectedRoute>
              }
            />

            {/* Fallback to dashboard (protected) */}
            <Route
              path="*"
              element={
                <ProtectedRoute requireAdmin>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />
          </Routes>
        </div>
      </div>
  );
}

export default Admin;
