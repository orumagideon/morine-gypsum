import axios from "axios";

// Use environment variable if available, otherwise default to local FastAPI server
const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

// Create an axios instance with common settings
const api = axios.create({
  baseURL,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
  withCredentials: false, // set to true if your backend uses cookies/sessions
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("authToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log errors but don't redirect (admin is now open access)
    if (error.response?.status === 401) {
      localStorage.removeItem("authToken");
    }
    return Promise.reject(error);
  }
);

// Export the instance as default (important for imports)
export default api;
