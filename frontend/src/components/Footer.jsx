import React from "react";
import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="site-footer mt-auto py-4">
      <div className="container d-flex flex-column flex-md-row justify-content-between align-items-center text-center text-md-start">
        <div className="mb-3 mb-md-0">
          <h5 className="mb-1 fw-bold text-light">Morine Gypsum</h5>
          <p className="text-muted small mb-0">
            Quality building materials · Reliable delivery
          </p>
        </div>

        <div className="footer-links d-flex gap-3 flex-wrap justify-content-center">
          <Link to="/" className="footer-link">Home</Link>
          <Link to="/store" className="footer-link">Store</Link>
          <Link to="/admin/login" className="footer-link">Admin</Link>
        </div>

        <div className="text-muted small mt-3 mt-md-0">
          © {new Date().getFullYear()} Morine Gypsum. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
