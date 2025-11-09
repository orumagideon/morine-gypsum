import React, { useState, useEffect } from "react";
import api from "../../api/axios";
import { getSettings, saveSettings, defaultSettings } from "../../config/settings";

export default function Settings() {
  const [settings, setSettings] = useState(getSettings());
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });

  const handleChange = (section, key, value) => {
    setSettings((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value,
      },
    }));
  };

  const handleNestedChange = (section, parentKey, key, value) => {
    setSettings((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [parentKey]: {
          ...prev[section][parentKey],
          [key]: value,
        },
      },
    }));
  };

  const handleSave = async () => {
    setLoading(true);
    setMessage({ type: "", text: "" });

    try {
      // Save to localStorage
      saveSettings(settings);

      // Also send to backend to update admin credentials if changed
      if (settings.admin.email !== defaultSettings.admin.email ||
          settings.admin.password !== defaultSettings.admin.password) {
        try {
          await api.post("/admin/update-credentials", {
            email: settings.admin.email,
            password: settings.admin.password,
          });
        } catch (err) {
          console.error("Failed to update credentials on backend:", err);
          // Still save locally even if backend update fails
        }
      }

      setMessage({ type: "success", text: "Settings saved successfully!" });
      setTimeout(() => setMessage({ type: "", text: "" }), 3000);
    } catch (error) {
      console.error("Failed to save settings:", error);
      setMessage({ type: "danger", text: "Failed to save settings" });
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    if (window.confirm("Are you sure you want to reset to default settings?")) {
      setSettings(defaultSettings);
      saveSettings(defaultSettings);
      setMessage({ type: "info", text: "Settings reset to defaults" });
      setTimeout(() => setMessage({ type: "", text: "" }), 3000);
    }
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>System Settings</h2>
        <div>
          <button
            className="btn btn-secondary me-2"
            onClick={handleReset}
            disabled={loading}
          >
            Reset to Defaults
          </button>
          <button
            className="btn btn-primary"
            onClick={handleSave}
            disabled={loading}
          >
            {loading ? "Saving..." : "Save Settings"}
          </button>
        </div>
      </div>

      {message.text && (
        <div className={`alert alert-${message.type}`} role="alert">
          {message.text}
        </div>
      )}

      <div className="row">
        <div className="col-md-6 mb-4">
          <div className="card">
            <div className="card-header">
              <h5>Admin Credentials</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <label className="form-label">Admin Email *</label>
                <input
                  type="email"
                  className="form-control"
                  value={settings.admin.email}
                  onChange={(e) =>
                    handleChange("admin", "email", e.target.value)
                  }
                  required
                />
                <small className="text-muted">
                  Email address for admin login and notifications
                </small>
              </div>
              <div className="mb-3">
                <label className="form-label">Admin Password *</label>
                <input
                  type="password"
                  className="form-control"
                  value={settings.admin.password}
                  onChange={(e) =>
                    handleChange("admin", "password", e.target.value)
                  }
                  required
                />
                <small className="text-muted">
                  Password for admin login (will be hashed on backend)
                </small>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-6 mb-4">
          <div className="card">
            <div className="card-header">
              <h5>MPESA Payment Settings</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <label className="form-label">Business Number *</label>
                <input
                  type="text"
                  className="form-control"
                  value={settings.payment.mpesa.businessNumber}
                  onChange={(e) =>
                    handleNestedChange(
                      "payment",
                      "mpesa",
                      "businessNumber",
                      e.target.value
                    )
                  }
                  required
                />
                <small className="text-muted">
                  Your Pochi la Biashara number
                </small>
              </div>
              <div className="mb-3">
                <label className="form-label">Payment Type *</label>
                <select
                  className="form-select"
                  value={settings.payment.mpesa.type}
                  onChange={(e) =>
                    handleNestedChange("payment", "mpesa", "type", e.target.value)
                  }
                >
                  <option value="pochi_la_biashara">Pochi la Biashara</option>
                  <option value="paybill">Paybill</option>
                  <option value="buy_goods">Buy Goods</option>
                </select>
              </div>
              {settings.payment.mpesa.type === "paybill" && (
                <div className="mb-3">
                  <label className="form-label">Account Number</label>
                  <input
                    type="text"
                    className="form-control"
                    value={settings.payment.mpesa.accountNumber || ""}
                    onChange={(e) =>
                      handleNestedChange(
                        "payment",
                        "mpesa",
                        "accountNumber",
                        e.target.value
                      )
                    }
                    placeholder="Optional account number"
                  />
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="col-md-6 mb-4">
          <div className="card">
            <div className="card-header">
              <h5>Email Notifications</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <label className="form-label">Admin Notification Email *</label>
                <input
                  type="email"
                  className="form-control"
                  value={settings.notifications.adminEmail}
                  onChange={(e) =>
                    handleChange("notifications", "adminEmail", e.target.value)
                  }
                  required
                />
                <small className="text-muted">
                  Email address to receive order and payment notifications
                </small>
              </div>
              <div className="mb-3">
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={settings.notifications.sendOrderNotifications}
                    onChange={(e) =>
                      handleChange(
                        "notifications",
                        "sendOrderNotifications",
                        e.target.checked
                      )
                    }
                    id="orderNotifications"
                  />
                  <label className="form-check-label" htmlFor="orderNotifications">
                    Send email notifications for new orders
                  </label>
                </div>
              </div>
              <div className="mb-3">
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    checked={settings.notifications.sendPaymentNotifications}
                    onChange={(e) =>
                      handleChange(
                        "notifications",
                        "sendPaymentNotifications",
                        e.target.checked
                      )
                    }
                    id="paymentNotifications"
                  />
                  <label className="form-check-label" htmlFor="paymentNotifications">
                    Send email notifications for payment confirmations
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

