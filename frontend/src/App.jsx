import React from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Home from "./pages/Home";
import Store from "./pages/Store";
import ProductDetail from "./components/ProductDetail";
import Cart from "./components/Cart";
import Checkout from "./components/Checkout";
import OrderDetail from "./pages/OrderDetail";
import OrderHistory from "./pages/OrderHistory";
import Admin from "./pages/Admin";
import Header from "./components/Header";
import Footer from "./components/Footer";

function AppContent() {
  const location = useLocation();
  const isAdminPage = location.pathname.startsWith("/admin");

  return (
    <AuthProvider>
      <Header />
      <main className={`container mt-4 content-wrap${isAdminPage ? " admin-content-wrap" : ""}`}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/store" element={<Store />} />
          <Route path="/products/:id" element={<ProductDetail />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/orders" element={<OrderHistory />} />
          <Route path="/orders/:id" element={<OrderDetail />} />
          <Route path="/admin/*" element={<Admin />} />
        </Routes>
      </main>
      <Footer />
    </AuthProvider>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
