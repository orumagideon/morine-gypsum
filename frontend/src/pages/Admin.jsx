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
  const isLoginRoute = location.pathname.endsWith("/login");

  return (
    <div className="admin-page">
      {!isLoginRoute && (
        <nav className="admin-subnav" aria-label="Admin navigation">
          <Link
            className={location.pathname === "/admin/dashboard" ? "active" : ""}
            to="/admin/dashboard"
          >
            Dashboard
          </Link>
          <Link
            className={location.pathname === "/admin/products" ? "active" : ""}
            to="/admin/products"
          >
            Products
          </Link>
          <Link
            className={location.pathname === "/admin/categories" ? "active" : ""}
            to="/admin/categories"
          >
            Categories
          </Link>
          <Link
            className={location.pathname === "/admin/orders" ? "active" : ""}
            to="/admin/orders"
          >
            Orders
          </Link>
          <Link
            className={location.pathname === "/admin/settings" ? "active" : ""}
            to="/admin/settings"
          >
            Settings
          </Link>
        </nav>
      )}

      <Routes>
        <Route path="login" element={<AdminLogin />} />
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
  );
}

export default Admin;
