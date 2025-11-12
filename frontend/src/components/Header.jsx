import React, { useContext, useState } from "react";
import { Link } from "react-router-dom";
import { CartContext } from "../context/CartContext";

export default function Header() {
  const { getItemCount } = useContext(CartContext);
  const cartCount = getItemCount();
  const [drawerOpen, setDrawerOpen] = useState(false);

  const toggleDrawer = () => setDrawerOpen((s) => !s);

  return (
    <header className="site-header">
      <nav className="navbar navbar-expand-lg navbar-light px-3">
        <div className="container-fluid">
          <Link className="navbar-brand logo d-flex align-items-center" to="/">
            <img src="/logo.svg" alt="Morine Gypsum" className="site-logo me-2" />
            <span className="brand-text">Morine Gypsum</span>
          </Link>

          <button
            className="navbar-toggler"
            type="button"
            aria-label="Toggle navigation"
            onClick={toggleDrawer}
          >
            <span className="navbar-toggler-icon"></span>
          </button>

          <div className={`collapse navbar-collapse ${drawerOpen ? "open" : ""}`} id="navbarNav">
            <ul className="navbar-nav me-auto">
              <li className="nav-item">
                <Link className="nav-link d-flex align-items-center" to="/">
                  <img src="/home.svg" alt="Home" className="nav-icon me-2" />
                  Home
                </Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link d-flex align-items-center" to="/store">
                  <img src="/building-store.svg" alt="Store" className="nav-icon me-2" />
                  Store
                </Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link d-flex align-items-center" to="/orders">
                  <img src="/My%20orders.svg" alt="Orders" className="nav-icon me-2" />
                  My Orders
                </Link>
              </li>
            </ul>

            <ul className="navbar-nav">
              <li className="nav-item">
                <Link className="nav-link position-relative d-flex align-items-center" to="/cart">
                  <img src="/shopping-cart-check.svg" alt="Cart" className="nav-icon me-2" />
                  Cart
                  {cartCount > 0 && (
                    <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                      {cartCount}
                    </span>
                  )}
                </Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link d-flex align-items-center" to="/admin/dashboard">
                  <img src="/admin%20settings.svg" alt="Admin" className="nav-icon me-2" />
                  Admin
                </Link>
              </li>
            </ul>
          </div>
          {/* Mobile slide-out drawer overlay */}
          <div className={`mobile-drawer ${drawerOpen ? "open" : ""}`} onClick={() => setDrawerOpen(false)}>
            <div className="mobile-drawer-panel" onClick={(e) => e.stopPropagation()}>
              <button className="btn-close" aria-label="Close" onClick={() => setDrawerOpen(false)}></button>
              <ul className="navbar-nav">
                <li className="nav-item">
                  <Link className="nav-link" to="/" onClick={() => setDrawerOpen(false)}>
                    Home
                  </Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/store" onClick={() => setDrawerOpen(false)}>
                    Store
                  </Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/orders" onClick={() => setDrawerOpen(false)}>
                    My Orders
                  </Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/cart" onClick={() => setDrawerOpen(false)}>
                    Cart
                  </Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/admin/dashboard" onClick={() => setDrawerOpen(false)}>
                    Admin
                  </Link>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </nav>
    </header>
  );
}
