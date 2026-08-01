import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { defaultSettings } from "../config/settings";

export default function AdminLogin() {
  const [loginEmail, setLoginEmail] = useState(defaultSettings.admin.email);
  const [loginPassword, setLoginPassword] = useState("");
  const [resetEmail, setResetEmail] = useState(defaultSettings.admin.email);
  const [resetCode, setResetCode] = useState("");
  const [resetPasswordValue, setResetPasswordValue] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [devResetCode, setDevResetCode] = useState("");
  const [showResetForm, setShowResetForm] = useState(false);
  const [resetStep, setResetStep] = useState("request");
  const [loading, setLoading] = useState(false);
  const { login, requestPasswordReset, resetPassword } = useContext(AuthContext);
  const navigate = useNavigate();

  const clearMessages = () => {
    setError("");
    setMessage("");
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    clearMessages();
    setLoading(true);

    const result = await login(loginEmail, loginPassword);
    if (result.success) {
      navigate("/admin/dashboard");
    } else {
      setError(result.error || "Invalid credentials");
    }

    setLoading(false);
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    clearMessages();
    setLoading(true);
    const emailToUse = resetEmail || loginEmail || defaultSettings.admin.email;
    setResetEmail(emailToUse);

    const result = await requestPasswordReset(emailToUse);
    if (result.success) {
      setShowResetForm(true);
      setResetStep("code");
      setDevResetCode(result.data?.dev_reset_code || "");
      setResetCode("");
      setResetPasswordValue("");
      setMessage(
        result.data?.dev_reset_code
          ? "Password reset code generated for the registered email. Use the code shown below to reset the password."
          : "Password reset code sent to your registered email."
      );
    } else {
      setError(result.error || "Password reset request failed");
    }

    setLoading(false);
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    clearMessages();
    setLoading(true);

    const result = await resetPassword(resetEmail, resetCode, resetPasswordValue);
    if (result.success) {
      setShowResetForm(false);
      setResetStep("request");
      setDevResetCode("");
      setMessage("Password reset successfully. You can log in now.");
    } else {
      setError(result.error || "Password reset failed");
    }

    setLoading(false);
  };

  return (
    <div className="container auth-page py-4">
      <div className="row justify-content-center">
        <div className="col-12 col-lg-8 col-xl-6">
          <div className="card shadow-lg border-0 auth-panel">
            <div className="card-body p-4 p-md-5">
              <div className="mb-4">
                <h1 className="auth-title auth-title--compact">Admin Login</h1>
                <p className="auth-copy auth-copy--compact mb-0">Use your admin email and password. Reset is available below if needed.</p>
              </div>

              {error && (
                <div className="alert alert-danger" role="alert">
                  {error}
                </div>
              )}
              {message && (
                <div className="alert alert-success" role="alert">
                  {message}
                </div>
              )}

              <form onSubmit={handleLogin} className="mb-4">
                <div className="mb-3">
                  <label htmlFor="loginEmail" className="form-label">Email</label>
                  <input id="loginEmail" type="email" className="form-control" value={loginEmail} onChange={(e) => setLoginEmail(e.target.value)} required autoFocus />
                </div>
                <div className="mb-3">
                  <label htmlFor="loginPassword" className="form-label">Password</label>
                  <input id="loginPassword" type="password" className="form-control" value={loginPassword} onChange={(e) => setLoginPassword(e.target.value)} required />
                </div>
                <button type="submit" className="btn btn-primary w-100" disabled={loading}>{loading ? "Logging in..." : "Login"}</button>
              </form>

              <hr className="my-4" />

              {!showResetForm ? (
                <button
                  type="button"
                  className="btn btn-outline-dark w-100"
                  onClick={() => {
                    setResetEmail(loginEmail || defaultSettings.admin.email);
                    setShowResetForm(true);
                    setResetStep("request");
                    clearMessages();
                  }}
                >
                  Forgot password?
                </button>
              ) : (
                <form onSubmit={resetStep === "code" ? handleResetPassword : handleForgotPassword}>
                  <h2 className="card-title mb-3">Reset Password</h2>
                  <div className="mb-3">
                    <label className="form-label">Email</label>
                    <input type="email" className="form-control" value={resetEmail} onChange={(e) => setResetEmail(e.target.value)} required />
                  </div>
                  {resetStep === "request" ? (
                    <button type="submit" className="btn btn-dark w-100" disabled={loading}>
                      {loading ? "Working..." : "Send Reset Code"}
                    </button>
                  ) : (
                    <>
                      <div className="mb-3">
                        <label className="form-label">Reset Code</label>
                        <input type="text" className="form-control" value={resetCode} onChange={(e) => setResetCode(e.target.value)} required />
                      </div>
                      <div className="mb-3">
                        <label className="form-label">New Password</label>
                        <input type="password" className="form-control" value={resetPasswordValue} onChange={(e) => setResetPasswordValue(e.target.value)} required />
                      </div>
                      <button type="submit" className="btn btn-dark w-100" disabled={loading}>
                        {loading ? "Working..." : "Reset Password"}
                      </button>
                    </>
                  )}
                  <button
                    type="button"
                    className="btn btn-link px-0 mt-2"
                    onClick={() => {
                      setShowResetForm(false);
                      setResetStep("request");
                      setDevResetCode("");
                      setResetCode("");
                      setResetPasswordValue("");
                      setResetEmail(defaultSettings.admin.email);
                    }}
                  >
                    Back to login
                  </button>
                </form>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

