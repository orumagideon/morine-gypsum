import React, { useContext, useState } from "react";
import { Link } from "react-router-dom";
import { CartContext } from "../context/CartContext";

const navigationItems = [
  { label: "Home", to: "/", icon: "/home.svg", alt: "Home" },
  { label: "Store", to: "/#store", icon: "/building-store.svg", alt: "Store" },
  { label: "My Orders", to: "/orders", icon: "/My%20orders.svg", alt: "Orders" },
  { label: "Cart", to: "/cart", icon: "/shopping-cart-check.svg", alt: "Cart" },
  { label: "Admin", to: "/admin/dashboard", icon: "/admin%20settings.svg", alt: "Admin" },
];

export default function Header() {
  const { getItemCount } = useContext(CartContext);
  const cartCount = getItemCount();
  const [drawerOpen, setDrawerOpen] = useState(false);

  const closeDrawer = () => setDrawerOpen(false);

  const renderLinks = (mobile = false) =>
    navigationItems.map(({ label, to, icon, alt }) => (
      <li className="nav-item" key={label}>
        <Link
          className="nav-link d-flex align-items-center"
          to={to}
          onClick={mobile ? closeDrawer : undefined}
        >
          <img src={icon} alt={alt} className="nav-icon me-2" />
          {label}
          {label === "Cart" && cartCount > 0 && (
            <span className="badge rounded-pill bg-danger ms-2">{cartCount}</span>
          )}
        </Link>
      </li>
    ));

  return (
    <header className="site-header">
      <nav className="navbar navbar-expand-lg navbar-light px-3">
        <div className="container-fluid">
          <Link className="navbar-brand logo d-flex align-items-center" to="/" onClick={closeDrawer}>
            <img src="/logo.svg" alt="Morine Gypsum" className="site-logo me-2" />
            <span className="brand-text">Morine Gypsum</span>
          </Link>

          <button
            className="navbar-toggler"
            type="button"
            aria-label={drawerOpen ? "Close navigation menu" : "Open navigation menu"}
            aria-expanded={drawerOpen}
            aria-controls="mobile-navigation"
            onClick={() => setDrawerOpen((open) => !open)}
          >
            <span className="navbar-toggler-icon" />
          </button>

          <div className="collapse navbar-collapse">
            <ul className="navbar-nav me-auto">{renderLinks()}</ul>
          </div>
        </div>
      </nav>

      {drawerOpen && (
        <div
          className="mobile-drawer"
          id="mobile-navigation"
          onClick={closeDrawer}
        >
          <nav
            className="mobile-drawer-panel"
            aria-label="Mobile navigation"
            onClick={(event) => event.stopPropagation()}
          >
            <ul className="navbar-nav">{renderLinks(true)}</ul>
          </nav>
        </div>
      )}
    </header>
  );
}
