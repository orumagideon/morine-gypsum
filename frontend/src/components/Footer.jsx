import React from "react";
import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="site-footer py-4">
      <div className="container d-flex flex-column flex-md-row justify-content-between align-items-center">
        <div className="mb-3 mb-md-0">
          <strong>Morine Gypsum</strong>
          <div className="text-muted small">Quality building materials · Reliable delivery</div>
        </div>

        <div className="d-flex gap-3">
          <Link to="/" className="text-decoration-none text-muted">Home</Link>
          <Link to="/store" className="text-decoration-none text-muted">Store</Link>
          <Link to="/admin/login" className="text-decoration-none text-muted">Admin</Link>
        </div>

        <div className="text-muted small">© {new Date().getFullYear()} Morine Gypsum. All rights reserved.</div>
      </div>
    </footer>
  );
}
