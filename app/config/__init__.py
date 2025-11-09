# app/config/__init__.py
import json
import os

def get_settings():
    """Load settings from environment or return defaults."""
    settings_file = os.getenv("SETTINGS_FILE", "app_settings.json")
    default_settings = {
        "admin": {
            "email": "orumagideon535@gmail.com",
            "password": "@Kisumu254"
        },
        "payment": {
            "mpesa": {
                "businessNumber": "0700183022",
                "type": "pochi_la_biashara",
                "accountNumber": ""
            }
        },
        "notifications": {
            "adminEmail": "orumagideon535@gmail.com",
            "sendOrderNotifications": True,
            "sendPaymentNotifications": True
        }
    }
    
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r") as f:
                saved = json.load(f)
                return {**default_settings, **saved}
        except:
            pass
    
    return default_settings

