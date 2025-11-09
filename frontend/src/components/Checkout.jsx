import React, { useContext, useState } from "react";
import { CartContext } from "../context/CartContext";
import api from "../api/axios";
import { useNavigate } from "react-router-dom";
import MpesaVerification from "./Checkout/MpesaVerification";
import { getMpesaBusinessNumber } from "../config/settings";

export default function Checkout() {
  const { items, clearCart, getTotal } = useContext(CartContext);
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [orderId, setOrderId] = useState(null);
  const [paymentVerified, setPaymentVerified] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    address: "",
    city: "",
    postalCode: "",
    paymentMethod: "mpesa", // Default to MPESA
    notes: "",
  });
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const validateStep1 = () => {
    return formData.name && formData.phone && formData.address;
  };

  const validateStep2 = () => {
    return formData.city && formData.postalCode;
  };

  const handleNext = () => {
    if (step === 1 && validateStep1()) {
      setStep(2);
    } else if (step === 2 && validateStep2()) {
      setStep(3);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  async function submitOrder(e) {
    e.preventDefault();
    if (items.length === 0) {
      alert("Your cart is empty!");
      return;
    }

    setLoading(true);
    const subtotal = getTotal();
    const shipping = 500;
    const total = subtotal + shipping;

    const payload = {
      customer_name: formData.name,
      customer_email: formData.email || null,
      customer_phone: formData.phone,
      delivery_address: `${formData.address}, ${formData.city}, ${formData.postalCode}`,
      payment_method: formData.paymentMethod,
      notes: formData.notes,
      total_amount: total,
      items: items.map((it) => ({
        product_id: it.product.id,
        quantity: it.qty,
        price: it.product.price,
      })),
      // Email notification settings
      send_email_to_customer: !!formData.email,
      send_email_to_admin: true,
    };

    try {
      const res = await api.post("/orders/", payload);
      const newOrderId = res.data.id;
      setOrderId(newOrderId);

      // If MPESA payment, go to verification step
      if (formData.paymentMethod === "mpesa") {
        setStep(4); // Go to MPESA verification step
      } else {
        // For other payment methods, complete order
        await completeOrder(newOrderId);
      }
    } catch (err) {
      console.error(err);
      alert(
        err.response?.data?.detail || "Failed to place order. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  async function completeOrder(orderId) {
    try {
      // Generate receipt/invoice
      if (!formData.email) {
        // Generate receipt for customer without email
        const receiptRes = await api.get(`/orders/${orderId}/receipt`, {
          responseType: "blob",
        });
        const url = window.URL.createObjectURL(new Blob([receiptRes.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", `receipt-${orderId}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
      }

      clearCart();
      alert("Order placed successfully! Order ID: #" + orderId);
      navigate(`/orders/${orderId}`);
    } catch (err) {
      console.error("Error completing order:", err);
      // Still navigate even if receipt generation fails
      clearCart();
      navigate(`/orders/${orderId}`);
    }
  }

  const handlePaymentVerified = async (verificationData) => {
    setPaymentVerified(true);
    await completeOrder(orderId);
  };

  const handleCancelPayment = () => {
    if (window.confirm("Are you sure you want to cancel? Your order will be saved but payment will be pending.")) {
      navigate(`/orders/${orderId}`);
    }
  };

  const subtotal = getTotal();
  const shipping = 500; // Fixed shipping cost
  const total = subtotal + shipping;

  return (
    <div className="container">
      <h2 className="mb-4">Checkout</h2>

      {/* Progress Indicator */}
      <div className="mb-4">
        <div className="d-flex justify-content-between">
          <div className={`step ${step >= 1 ? "active" : ""}`}>
            <span className="badge bg-primary">1</span> Customer Info
          </div>
          <div className={`step ${step >= 2 ? "active" : ""}`}>
            <span className="badge bg-primary">2</span> Shipping Details
          </div>
          <div className={`step ${step >= 3 ? "active" : ""}`}>
            <span className="badge bg-primary">3</span> Review & Payment
          </div>
          {formData.paymentMethod === "mpesa" && (
            <div className={`step ${step >= 4 ? "active" : ""}`}>
              <span className="badge bg-primary">4</span> MPESA Verify
            </div>
          )}
        </div>
      </div>

      <div className="row">
        <div className="col-md-8">
          <div className="card">
            <div className="card-body">
              {step === 1 && (
                <div>
                  <h4 className="mb-3">Customer Information</h4>
                  <div className="mb-3">
                    <label className="form-label">Full Name *</label>
                    <input
                      type="text"
                      className="form-control"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Email</label>
                    <input
                      type="email"
                      className="form-control"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Phone Number *</label>
                    <input
                      type="tel"
                      className="form-control"
                      name="phone"
                      value={formData.phone}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Delivery Address *</label>
                    <textarea
                      className="form-control"
                      name="address"
                      value={formData.address}
                      onChange={handleInputChange}
                      rows="3"
                      required
                    />
                  </div>
                  <button
                    className="btn btn-primary"
                    onClick={handleNext}
                    disabled={!validateStep1()}
                  >
                    Next
                  </button>
                </div>
              )}

              {step === 2 && (
                <div>
                  <h4 className="mb-3">Shipping Details</h4>
                  <div className="mb-3">
                    <label className="form-label">City *</label>
                    <input
                      type="text"
                      className="form-control"
                      name="city"
                      value={formData.city}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Postal Code *</label>
                    <input
                      type="text"
                      className="form-control"
                      name="postalCode"
                      value={formData.postalCode}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Order Notes</label>
                    <textarea
                      className="form-control"
                      name="notes"
                      value={formData.notes}
                      onChange={handleInputChange}
                      rows="3"
                      placeholder="Any special instructions..."
                    />
                  </div>
                  <div className="d-flex gap-2">
                    <button className="btn btn-secondary" onClick={handleBack}>
                      Back
                    </button>
                    <button
                      className="btn btn-primary"
                      onClick={handleNext}
                      disabled={!validateStep2()}
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}

              {step === 3 && (
                <form onSubmit={submitOrder}>
                  <h4 className="mb-3">Review & Payment</h4>
                  <div className="mb-3">
                    <label className="form-label">Payment Method *</label>
                    <select
                      className="form-select"
                      name="paymentMethod"
                      value={formData.paymentMethod}
                      onChange={handleInputChange}
                      required
                    >
                      <option value="mpesa">MPESA (Pochi la Biashara)</option>
                      <option value="cash_on_delivery">Cash on Delivery</option>
                      <option value="bank_transfer">Bank Transfer</option>
                    </select>
                    {formData.paymentMethod === "mpesa" && (
                      <div className="alert alert-info mt-2 mb-0">
                        <small>
                          <strong>Business Number:</strong> {getMpesaBusinessNumber()}
                          <br />
                          You will be asked to verify your payment after placing the order.
                        </small>
                      </div>
                    )}
                  </div>

                  <div className="card bg-light mb-3">
                    <div className="card-body">
                      <h5>Order Summary</h5>
                      {items.map((item) => (
                        <div
                          key={item.product.id}
                          className="d-flex justify-content-between mb-2"
                        >
                          <span>
                            {item.product.name} x {item.qty}
                          </span>
                          <span>
                            KES {(item.product.price * item.qty).toLocaleString()}
                          </span>
                        </div>
                      ))}
                      <hr />
                      <div className="d-flex justify-content-between">
                        <span>Subtotal:</span>
                        <span>KES {subtotal.toLocaleString()}</span>
                      </div>
                      <div className="d-flex justify-content-between">
                        <span>Shipping:</span>
                        <span>KES {shipping.toLocaleString()}</span>
                      </div>
                      <hr />
                      <div className="d-flex justify-content-between">
                        <strong>Total:</strong>
                        <strong>KES {total.toLocaleString()}</strong>
                      </div>
                    </div>
                  </div>

                  <div className="d-flex gap-2">
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={handleBack}
                    >
                      Back
                    </button>
                    <button
                      type="submit"
                      className="btn btn-success"
                      disabled={loading}
                    >
                      {loading ? "Placing Order..." : "Place Order"}
                    </button>
                  </div>
                </form>
              )}

              {step === 4 && formData.paymentMethod === "mpesa" && (
                <div>
                  <MpesaVerification
                    phoneNumber={formData.phone}
                    amount={total}
                    onVerified={handlePaymentVerified}
                    onCancel={handleCancelPayment}
                    orderId={orderId}
                  />
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card">
            <div className="card-body">
              <h5>Order Summary</h5>
              {items.map((item) => (
                <div key={item.product.id} className="mb-2">
                  <div className="d-flex justify-content-between">
                    <small>{item.product.name}</small>
                    <small>KES {item.product.price * item.qty}</small>
                  </div>
                  <small className="text-muted">Qty: {item.qty}</small>
                </div>
              ))}
              <hr />
              <div className="d-flex justify-content-between">
                <span>Subtotal:</span>
                <span>KES {subtotal.toLocaleString()}</span>
              </div>
              <div className="d-flex justify-content-between">
                <span>Shipping:</span>
                <span>KES {shipping.toLocaleString()}</span>
              </div>
              <hr />
              <div className="d-flex justify-content-between">
                <strong>Total:</strong>
                <strong>KES {total.toLocaleString()}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
