import React from "react";
import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="site-footer mt-auto py-2">
      <div className="container footer-content d-flex flex-column flex-md-row justify-content-between align-items-center text-center text-md-start">
        <div className="footer-brand">
          <h5 className="mb-1 fw-bold footer-heading">Morine Gypsum</h5>
          <p className="footer-copy small mb-0">Quality materials and reliable delivery.</p>
        </div>

        <div className="footer-links d-flex gap-3 flex-wrap justify-content-center">
          <Link to="/" className="footer-link">Home</Link>
          <Link to="/#store" className="footer-link">Store</Link>
          <Link to="/admin/login" className="footer-link">Admin</Link>
        </div>

        <div className="footer-copyright small">
          © {new Date().getFullYear()} Morine Gypsum. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
