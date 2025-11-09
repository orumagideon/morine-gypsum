// Application Configuration
// These settings can be updated through the admin panel

export const defaultSettings = {
  admin: {
    email: "orumagideon535@gmail.com",
    password: "@Kisumu254", // This should be hashed in production
  },
  payment: {
    mpesa: {
      businessNumber: "0700183022",
      type: "pochi_la_biashara", // Can be changed to "paybill" or "buy_goods" in future
      accountNumber: "", // Optional account number for paybill
    },
  },
  notifications: {
    adminEmail: "orumagideon535@gmail.com",
    sendOrderNotifications: true,
    sendPaymentNotifications: true,
  },
};

// Load settings from localStorage or use defaults
export function getSettings() {
  const saved = localStorage.getItem("appSettings");
  if (saved) {
    try {
      return { ...defaultSettings, ...JSON.parse(saved) };
    } catch (e) {
      console.error("Failed to parse settings:", e);
    }
  }
  return defaultSettings;
}

// Save settings to localStorage
export function saveSettings(settings) {
  localStorage.setItem("appSettings", JSON.stringify(settings));
}

// Get admin email
export function getAdminEmail() {
  return getSettings().notifications.adminEmail;
}

// Get MPESA business number
export function getMpesaBusinessNumber() {
  return getSettings().payment.mpesa.businessNumber;
}

