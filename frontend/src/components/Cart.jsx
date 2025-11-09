import React, { useContext } from "react";
import { CartContext } from "../context/CartContext";
import { Link } from "react-router-dom";
import api from "../api/axios";

export default function Cart() {
  const { items, updateQty, removeItem, getTotal } = useContext(CartContext);
  const total = getTotal();
  const shipping = 500;
  const grandTotal = total + shipping;

  return (
    <div className="container mt-4">
      <h2 className="mb-4">Shopping Cart</h2>

      {items.length === 0 ? (
        <div className="alert alert-info">
          <p>Your cart is empty.</p>
          <Link to="/store" className="btn btn-primary">
            Continue Shopping
          </Link>
        </div>
      ) : (
        <div className="row">
          <div className="col-md-8">
            <div className="card">
              <div className="card-body">
                {items.map((it) => (
                  <div
                    key={it.product.id}
                    className="d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom"
                  >
                    <div className="d-flex">
                      {it.product.image_url && (
                        <img
                          src={
                            it.product.image_url.startsWith("http")
                              ? it.product.image_url
                              : `${api.defaults.baseURL}${it.product.image_url}`
                          }
                          alt={it.product.name}
                          style={{
                            width: 80,
                            height: 80,
                            objectFit: "cover",
                            marginRight: 15,
                          }}
                        />
                      )}
                      <div>
                        <h6>{it.product.name}</h6>
                        <p className="text-muted mb-0">
                          KES {it.product.price?.toLocaleString()} each
                        </p>
                        {it.product.stock_quantity !== undefined && (
                          <small className="text-muted">
                            Stock: {it.product.stock_quantity}
                          </small>
                        )}
                      </div>
                    </div>
                    <div className="d-flex align-items-center gap-3">
                      <div className="d-flex align-items-center">
                        <button
                          onClick={() => updateQty(it.product.id, it.qty - 1)}
                          disabled={it.qty <= 1}
                          className="btn btn-sm btn-outline-secondary"
                        >
                          -
                        </button>
                        <span className="mx-3">{it.qty}</span>
                        <button
                          onClick={() => updateQty(it.product.id, it.qty + 1)}
                          className="btn btn-sm btn-outline-secondary"
                          disabled={
                            it.product.stock_quantity &&
                            it.qty >= it.product.stock_quantity
                          }
                        >
                          +
                        </button>
                      </div>
                      <div className="text-end" style={{ minWidth: 100 }}>
                        <strong>
                          KES {(it.product.price * it.qty).toLocaleString()}
                        </strong>
                      </div>
                      <button
                        onClick={() => removeItem(it.product.id)}
                        className="btn btn-sm btn-danger"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="col-md-4">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">Order Summary</h5>
                <div className="d-flex justify-content-between mb-2">
                  <span>Subtotal:</span>
                  <span>KES {total.toLocaleString()}</span>
                </div>
                <div className="d-flex justify-content-between mb-2">
                  <span>Shipping:</span>
                  <span>KES {shipping.toLocaleString()}</span>
                </div>
                <hr />
                <div className="d-flex justify-content-between mb-3">
                  <strong>Total:</strong>
                  <strong>KES {grandTotal.toLocaleString()}</strong>
                </div>
                <Link to="/checkout" className="btn btn-primary w-100">
                  Proceed to Checkout
                </Link>
                <Link
                  to="/store"
                  className="btn btn-outline-secondary w-100 mt-2"
                >
                  Continue Shopping
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
