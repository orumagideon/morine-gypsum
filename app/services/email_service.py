# app/services/email_service.py
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional
from app.config import get_settings

def send_email(
    to_email: str,
    subject: str,
    body: str,
    attachment_path: Optional[str] = None
) -> bool:
    """
    Send an email with optional PDF attachment.
    Returns True if successful, False otherwise.
    """
    try:
        settings = get_settings()
        
        # Email configuration - should be in environment variables
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME", settings.get("notifications", {}).get("adminEmail", "orumagideon535@gmail.com"))
        smtp_password = os.getenv("SMTP_PASSWORD", "")  # Should be app-specific password
        
        # If no password configured, skip email sending
        if not smtp_password:
            print(f"SMTP_PASSWORD not configured. Email to {to_email} would be sent with subject: {subject}")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg["From"] = smtp_username
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))
        
        # Add attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {os.path.basename(attachment_path)}"
                )
                msg.attach(part)
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, to_email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email to {to_email}: {str(e)}")
        return False


def send_order_notification(order_data: dict) -> bool:
    """Send order notification to admin."""
    settings = get_settings()
    admin_email = settings.get("notifications", {}).get("adminEmail", "orumagideon535@gmail.com")
    
    if not settings.get("notifications", {}).get("sendOrderNotifications", True):
        return False
    
    subject = f"New Order Received - Order #{order_data['id']}"
    body = f"""
    <html>
    <body>
        <h2>New Order Received</h2>
        <p><strong>Order ID:</strong> #{order_data['id']}</p>
        <p><strong>Customer:</strong> {order_data['customer_name']}</p>
        <p><strong>Phone:</strong> {order_data['customer_phone']}</p>
        <p><strong>Email:</strong> {order_data.get('customer_email', 'N/A')}</p>
        <p><strong>Delivery Address:</strong> {order_data['delivery_address']}</p>
        <p><strong>Total Amount:</strong> KES {order_data.get('total_amount', order_data.get('total_price', 0)):,.2f}</p>
        <p><strong>Payment Method:</strong> {order_data.get('payment_method', 'N/A')}</p>
        <p><strong>Status:</strong> {order_data.get('status', 'pending')}</p>
    </body>
    </html>
    """
    
    return send_email(admin_email, subject, body)


def send_payment_confirmation(order_data: dict) -> bool:
    """Send payment confirmation to admin and customer."""
    settings = get_settings()
    admin_email = settings.get("notifications", {}).get("adminEmail", "orumagideon535@gmail.com")
    
    # Send to admin
    if settings.get("notifications", {}).get("sendPaymentNotifications", True):
        subject = f"Payment Verified - Order #{order_data['id']}"
        body = f"""
        <html>
        <body>
            <h2>Payment Verified</h2>
            <p><strong>Order ID:</strong> #{order_data['id']}</p>
            <p><strong>Customer:</strong> {order_data['customer_name']}</p>
            <p><strong>Amount:</strong> KES {order_data.get('total_amount', order_data.get('total_price', 0)):,.2f}</p>
            <p><strong>Payment Method:</strong> {order_data.get('payment_method', 'N/A')}</p>
            <p><strong>MPESA Code:</strong> {order_data.get('mpesa_code', 'N/A')}</p>
        </body>
        </html>
        """
        send_email(admin_email, subject, body)
    
    # Send to customer if email provided
    customer_email = order_data.get('customer_email')
    if customer_email:
        subject = f"Payment Confirmed - Order #{order_data['id']}"
        body = f"""
        <html>
        <body>
            <h2>Payment Confirmed</h2>
            <p>Dear {order_data['customer_name']},</p>
            <p>Your payment for Order #{order_data['id']} has been verified.</p>
            <p><strong>Amount:</strong> KES {order_data.get('total_amount', order_data.get('total_price', 0)):,.2f}</p>
            <p>Thank you for your purchase!</p>
        </body>
        </html>
        """
        send_email(customer_email, subject, body)
    
    return True


def send_invoice_email(order_data: dict, invoice_path: str) -> bool:
    """Send invoice to customer email."""
    customer_email = order_data.get('customer_email')
    if not customer_email:
        return False
    
    subject = f"Invoice - Order #{order_data['id']}"
    body = f"""
    <html>
    <body>
        <h2>Your Invoice</h2>
        <p>Dear {order_data['customer_name']},</p>
        <p>Thank you for your order! Please find your invoice attached.</p>
        <p><strong>Order ID:</strong> #{order_data['id']}</p>
        <p><strong>Total Amount:</strong> KES {order_data.get('total_amount', order_data.get('total_price', 0)):,.2f}</p>
        <p>Best regards,<br>Morine Gypsum</p>
    </body>
    </html>
    """
    
    return send_email(customer_email, subject, body, invoice_path)

