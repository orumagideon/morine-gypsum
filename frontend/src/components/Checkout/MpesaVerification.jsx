import React, { useState, useEffect } from "react";
import { getMpesaBusinessNumber } from "../../config/settings";
import api from "../../api/axios";

export default function MpesaVerification({ 
  phoneNumber, 
  amount, 
  onVerified, 
  onCancel,
  orderId 
}) {
  const [mpesaCode, setMpesaCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [countdown, setCountdown] = useState(300); // 5 minutes
  const [pushRequested, setPushRequested] = useState(false);
  const [requestId, setRequestId] = useState(null);
  const [polling, setPolling] = useState(false);
  const businessNumber = getMpesaBusinessNumber();

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setError("");
    
    if (!mpesaCode || mpesaCode.length < 6) {
      setError("Please enter a valid MPESA confirmation code");
      return;
    }

    setLoading(true);
    try {
      // Call backend to verify MPESA payment
      const response = await api.post(`/orders/${orderId}/verify-payment`, {
        mpesa_code: mpesaCode,
        phone_number: phoneNumber,
      });
      
      if (response.data) {
        onVerified(response.data);
      } else {
        setError("Verification failed. Please check your code and try again.");
      }
    } catch (err) {
      console.error("Payment verification error:", err);
      setError(
        err.response?.data?.detail || 
        "Verification failed. Please check your code and try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const requestStkPush = async () => {
    setError("");
    setLoading(true);
    try {
      const res = await api.post(`/orders/${orderId}/mpesa/push`, {
        phone_number: phoneNumber,
        amount,
      });
      if (res.data && res.data.request_id) {
        setRequestId(res.data.request_id);
        setPushRequested(true);
        // start polling for status
        setPolling(true);
      } else {
        setError("Failed to initiate STK Push. Please try manual payment.");
      }
    } catch (err) {
      console.error("STK Push error:", err);
      setError("Failed to initiate STK Push. Please try manual payment.");
    } finally {
      setLoading(false);
    }
  };

  // Poll for status when pushRequested/polling is true
  useEffect(() => {
    if (!polling || !pushRequested) return;

    let cancelled = false;
    const interval = setInterval(async () => {
      try {
        const res = await api.get(`/orders/${orderId}/mpesa/status`);
        if (res.data && res.data.payment_verified) {
          if (!cancelled) {
            setPolling(false);
            setPushRequested(false);
            onVerified(res.data);
          }
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 5000);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [polling, pushRequested, orderId, onVerified]);

  return (
    <div className="card">
      <div className="card-body">
        <h4 className="mb-3">MPESA Payment Verification</h4>
        
        <div className="alert alert-info mb-3">
          <h6>Payment Instructions:</h6>
          <ol className="mb-0">
            <li>Go to your MPESA menu</li>
            <li>Select <strong>Lipa na M-PESA</strong></li>
            <li>Select <strong>Pochi la Biashara</strong></li>
            <li>Enter Business Number: <strong>{businessNumber}</strong></li>
            <li>Enter Amount: <strong>KES {amount.toLocaleString()}</strong></li>
            <li>Enter your MPESA PIN</li>
            <li>You will receive a confirmation message with a code</li>
          </ol>
        </div>

        <div className="alert alert-warning mb-3">
          <strong>Time Remaining:</strong> {formatTime(countdown)}
          {countdown < 60 && (
            <span className="text-danger ms-2">⚠️ Less than 1 minute left!</span>
          )}
        </div>

        {!pushRequested ? (
          <div className="mb-3">
            <button
              type="button"
              className="btn btn-primary"
              onClick={requestStkPush}
              disabled={loading}
            >
              {loading ? "Requesting…" : "Request STK Push (One-tap)"}
            </button>
            <small className="form-text text-muted mt-2">
              You can request an STK Push to your phone to pay without entering the MPESA code manually.
            </small>
          </div>
        ) : (
          <div className="alert alert-info mb-3">
            <p className="mb-1"><strong>STK Push Requested</strong></p>
            <p className="mb-1">Request ID: {requestId}</p>
            <p className="mb-0">Waiting for confirmation…</p>
          </div>
        )}

        <form onSubmit={handleVerify}>
          <div className="mb-3">
            <label className="form-label">
              Enter MPESA Confirmation Code *
            </label>
            <input
              type="text"
              className="form-control"
              placeholder="e.g., QH4RT8K9L2"
              value={mpesaCode}
              onChange={(e) => setMpesaCode(e.target.value.toUpperCase())}
              maxLength={10}
              required
              autoFocus
            />
            <small className="text-muted">
              Enter the confirmation code from your MPESA message
            </small>
          </div>

          {error && (
            <div className="alert alert-danger" role="alert">
              {error}
            </div>
          )}

          <div className="d-flex gap-2">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onCancel}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-success"
              disabled={loading || countdown === 0}
            >
              {loading ? "Verifying..." : "Verify Payment"}
            </button>
          </div>

          {countdown === 0 && (
            <div className="alert alert-danger mt-3">
              Time expired. Please restart the payment process.
            </div>
          )}
        </form>
      </div>
    </div>
  );
}

