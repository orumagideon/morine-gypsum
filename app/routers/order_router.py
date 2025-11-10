# app/routers/order_router.py
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlmodel import select, Session
from app.db.session import get_session
from app.models.models import Order, OrderItem, Product, Invoice
from app.schemas.schemas import OrderCreate, OrderRead, OrderUpdate, PaymentVerification
from app.utils.pdf_generator import generate_invoice_pdf
from app.services.email_service import (
    send_order_notification,
    send_payment_confirmation,
    send_invoice_email
)
from app.config import get_settings
import time
import uuid

router = APIRouter(prefix="/orders", tags=["Orders"])


# ===============================
# CREATE ORDER (with email notifications)
# ===============================
@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate, session: Session = Depends(get_session)):
    """Create an order, generate invoice, send notifications, and return details."""
    if not order_data.items:
        raise HTTPException(status_code=400, detail="Order must have at least one product")

    # Calculate totals
    subtotal = 0.0
    shipping_cost = 500.0
    total_amount = order_data.total_amount or 0.0

    # Initialize order
    order = Order(
        customer_name=order_data.customer_name,
        customer_email=order_data.customer_email,
        customer_phone=order_data.customer_phone,
        delivery_address=order_data.delivery_address,
        payment_method=order_data.payment_method or "cash_on_delivery",
        status="pending",
        payment_status="pending",
        notes=order_data.notes,
        created_at=datetime.utcnow(),
        total_price=0.0,
        shipping_cost=shipping_cost,
        total_amount=total_amount
    )
    session.add(order)
    session.commit()
    session.refresh(order)

    order_items = []

    # Process each product
    for item in order_data.items:
        product = session.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product ID {item.product_id} not found")

        if product.stock_quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")

        item_price = item.price if hasattr(item, 'price') and item.price else product.price
        total_price = item_price * item.quantity
        subtotal += total_price

        # Update product stock
        product.stock_quantity -= item.quantity
        session.add(product)

        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item_price
        )
        session.add(order_item)
        order_items.append(order_item)

    # Update order totals
    order.total_price = subtotal
    if not order_data.total_amount:
        order.total_amount = subtotal + shipping_cost
    session.add(order)
    session.commit()
    session.refresh(order)

    # ===============================
    # Create Invoice Record
    # ===============================
    new_invoice = Invoice(
        order_id=order.id,
        total_amount=order.total_amount,
        payment_method=order.payment_method,
        payment_status="Pending",
        invoice_date=datetime.utcnow()
    )
    session.add(new_invoice)
    session.commit()
    session.refresh(new_invoice)

    # ===============================
    # Generate PDF Invoice/Receipt
    # ===============================
    order_items_data = [
        {
            "name": session.get(Product, item.product_id).name,
            "quantity": item.quantity,
            "price": item.price
        }
        for item in order_items
    ]

    invoice_data = {
        "invoice_id": new_invoice.id,
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "delivery_address": order.delivery_address,
        "order_items": order_items_data,
        "total_price": order.total_amount,
        "invoice_date": new_invoice.invoice_date,
    }

    pdf_path = generate_invoice_pdf(invoice_data)
    new_invoice.remarks = f"PDF generated at: {pdf_path}"
    session.add(new_invoice)
    session.commit()

    # ===============================
    # Send Email Notifications
    # ===============================
    order_dict = {
        "id": order.id,
        "customer_name": order.customer_name,
        "customer_email": order.customer_email,
        "customer_phone": order.customer_phone,
        "delivery_address": order.delivery_address,
        "total_amount": order.total_amount,
        "total_price": order.total_price,
        "payment_method": order.payment_method,
        "status": order.status
    }

    # Send to admin
    if order_data.send_email_to_admin:
        send_order_notification(order_dict)

    # Send invoice to customer if email provided
    if order_data.send_email_to_customer and order.customer_email:
        send_invoice_email(order_dict, pdf_path)

    # Build a plain dict for the response to avoid setting relationship attributes
    order_items = session.exec(
        select(OrderItem).where(OrderItem.order_id == order.id)
    ).all()

    items_response = []
    for item in order_items:
        product = session.get(Product, item.product_id)
        items_response.append(
            {
                "id": item.id,
                "product_id": item.product_id,
                "product": {"id": product.id, "name": product.name, "price": product.price} if product else None,
                "quantity": item.quantity,
                "price": item.price,
            }
        )

    order_response = {
        "id": order.id,
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "customer_email": order.customer_email,
        "delivery_address": order.delivery_address,
        "status": order.status,
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "total_amount": order.total_amount,
        "total_price": order.total_price,
        "shipping_cost": order.shipping_cost,
        "created_at": order.created_at,
        "items": items_response,
    }

    return order_response


# ===============================
# VERIFY MPESA PAYMENT
# ===============================
@router.post("/{order_id}/verify-payment")
def verify_payment(
    order_id: int,
    verification: PaymentVerification,
    session: Session = Depends(get_session)
):
    """Verify MPESA payment with confirmation code."""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.payment_method != "mpesa":
        raise HTTPException(status_code=400, detail="Order is not using MPESA payment")

    if order.payment_verified:
        raise HTTPException(status_code=400, detail="Payment already verified")

    # In a real implementation, you would verify the MPESA code with Safaricom API
    # For now, we'll do basic validation (code should be alphanumeric, 6-10 chars)
    mpesa_code = verification.mpesa_code.strip().upper()
    if len(mpesa_code) < 6 or len(mpesa_code) > 10:
        raise HTTPException(status_code=400, detail="Invalid MPESA confirmation code format")

    # Verify phone number matches
    if order.customer_phone != verification.phone_number:
        raise HTTPException(
            status_code=400,
            detail="Phone number does not match order"
        )

    # Update order payment status
    order.mpesa_code = mpesa_code
    order.payment_verified = True
    order.payment_status = "verified"
    session.add(order)
    session.commit()
    session.refresh(order)

    # Update invoice
    invoice = session.exec(select(Invoice).where(Invoice.order_id == order_id)).first()
    if invoice:
        invoice.payment_status = "Paid"
        invoice.payment_method = "MPESA"
        session.add(invoice)
        session.commit()

    # Send payment confirmation emails
    order_dict = {
        "id": order.id,
        "customer_name": order.customer_name,
        "customer_email": order.customer_email,
        "customer_phone": order.customer_phone,
        "total_amount": order.total_amount,
        "total_price": order.total_price,
        "payment_method": order.payment_method,
        "mpesa_code": mpesa_code,
        "status": order.status
    }
    send_payment_confirmation(order_dict)

    return {
        "success": True,
        "message": "Payment verified successfully",
        "order_id": order.id,
        "payment_status": "verified"
    }


# ===============================
# INITIATE MPESA STK PUSH (Pochi / Simulation)
# ===============================
@router.post("/{order_id}/mpesa/push")
def initiate_mpesa_push(order_id: int, payload: dict, session: Session = Depends(get_session)):
    """Initiate an STK Push for the given order. If an external MPESA provider is configured
    (via settings/payment), this will attempt to call it; otherwise we simulate and return
    a request id. The frontend can poll the status endpoint or rely on webhook callbacks.
    Payload should include: phone_number (string) and optional amount (float).
    """
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    phone = payload.get("phone_number")
    amount = payload.get("amount") or order.total_amount or order.total_price
    if not phone:
        raise HTTPException(status_code=400, detail="phone_number is required")

    settings = get_settings()
    mpesa_cfg = settings.get("payment", {}).get("mpesa", {})

    # If real provider credentials are not configured, simulate a push request
    # and store a request reference on the order record.
    request_id = f"SIM-{order_id}-{int(time.time())}"
    order.mpesa_request_id = request_id
    session.add(order)
    session.commit()
    session.refresh(order)

    # In a real integration we'd call the provider here and return their request id
    return {"request_id": request_id, "message": "STK Push initiated (simulated)"}


# ===============================
# MPESA STATUS (for polling)
# ===============================
@router.get("/{order_id}/mpesa/status")
def mpesa_status(order_id: int, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "order_id": order.id,
        "payment_status": order.payment_status,
        "payment_verified": order.payment_verified,
        "mpesa_request_id": order.mpesa_request_id,
        "mpesa_code": order.mpesa_code,
    }


# ===============================
# MPESA WEBHOOK (called by provider when payment is confirmed)
# ===============================
@router.post("/mpesa/webhook")
def mpesa_webhook(payload: dict, session: Session = Depends(get_session)):
    """Receive MPESA payment confirmation callbacks from provider.
    Expected payload (varies by provider): {order_id, mpesa_code, phone_number, status, amount}
    This endpoint marks the order as paid/verified and sends notifications.
    """
    order_id = payload.get("order_id")
    mpesa_code = payload.get("mpesa_code")
    phone_number = payload.get("phone_number")
    status = payload.get("status", "SUCCESS")

    if not order_id:
        raise HTTPException(status_code=400, detail="order_id required")

    order = session.get(Order, int(order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Only accept successful statuses
    if str(status).upper() not in ("SUCCESS", "PAID", "COMPLETED"):
        return {"received": True, "message": "Ignored non-successful status"}

    # Update order
    order.mpesa_code = mpesa_code or order.mpesa_code
    order.payment_verified = True
    order.payment_status = "verified"
    session.add(order)
    session.commit()
    session.refresh(order)

    # Update invoice if present
    invoice = session.exec(select(Invoice).where(Invoice.order_id == order.id)).first()
    if invoice:
        invoice.payment_status = "Paid"
        invoice.payment_method = "MPESA"
        session.add(invoice)
        session.commit()

    # Send notifications
    order_dict = {
        "id": order.id,
        "customer_name": order.customer_name,
        "customer_email": order.customer_email,
        "customer_phone": order.customer_phone,
        "total_amount": order.total_amount,
        "total_price": order.total_price,
        "payment_method": order.payment_method,
        "mpesa_code": order.mpesa_code,
        "status": order.status,
    }
    send_payment_confirmation(order_dict)

    return {"received": True, "order_id": order.id}


# ===============================
# READ ALL ORDERS
# ===============================
@router.get("/", response_model=list[OrderRead])
def get_orders(session: Session = Depends(get_session)):
    """Get all orders with their items."""
    orders = session.exec(select(Order)).all()
    result = []
    # Build plain serializable dicts for each order
    for order in orders:
        order_items = session.exec(
            select(OrderItem).where(OrderItem.order_id == order.id)
        ).all()

        items_response = []
        for item in order_items:
            product = session.get(Product, item.product_id)
            items_response.append(
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "product": {"id": product.id, "name": product.name, "price": product.price} if product else None,
                    "quantity": item.quantity,
                    "price": item.price,
                }
            )

        result.append(
            {
                "id": order.id,
                "customer_name": order.customer_name,
                "customer_phone": order.customer_phone,
                "customer_email": order.customer_email,
                "delivery_address": order.delivery_address,
                "status": order.status,
                "payment_method": order.payment_method,
                "payment_status": order.payment_status,
                "total_amount": order.total_amount,
                "total_price": order.total_price,
                "shipping_cost": order.shipping_cost,
                "created_at": order.created_at,
                "items": items_response,
            }
        )

    return result


# ===============================
# READ SINGLE ORDER
# ===============================
@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, session: Session = Depends(get_session)):
    """Get a single order with its items."""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Load order items with product details
    order_items = session.exec(
        select(OrderItem).where(OrderItem.order_id == order_id)
    ).all()
    
    # Build serializable response dict
    items_response = []
    for item in order_items:
        product = session.get(Product, item.product_id)
        items_response.append(
            {
                "id": item.id,
                "product_id": item.product_id,
                "product": {"id": product.id, "name": product.name, "price": product.price} if product else None,
                "quantity": item.quantity,
                "price": item.price,
            }
        )

    order_response = {
        "id": order.id,
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "customer_email": order.customer_email,
        "delivery_address": order.delivery_address,
        "status": order.status,
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "total_amount": order.total_amount,
        "total_price": order.total_price,
        "shipping_cost": order.shipping_cost,
        "created_at": order.created_at,
        "items": items_response,
    }

    return order_response


# ===============================
# UPDATE ORDER STATUS
# ===============================
@router.patch("/{order_id}", response_model=OrderRead)
def update_order(
    order_id: int,
    order_update: OrderUpdate,
    session: Session = Depends(get_session)
):
    """Update an order (status, payment status, etc.)."""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    update_data = order_update.dict(exclude_unset=True)
    previous_status = order.status
    for key, value in update_data.items():
        setattr(order, key, value)

    session.add(order)
    session.commit()
    session.refresh(order)
    
    # Build response dict including items
    order_items = session.exec(
        select(OrderItem).where(OrderItem.order_id == order_id)
    ).all()

    items_response = []
    for item in order_items:
        product = session.get(Product, item.product_id)
        items_response.append(
            {
                "id": item.id,
                "product_id": item.product_id,
                "product": {"id": product.id, "name": product.name, "price": product.price} if product else None,
                "quantity": item.quantity,
                "price": item.price,
            }
        )

    order_response = {
        "id": order.id,
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "customer_email": order.customer_email,
        "delivery_address": order.delivery_address,
        "status": order.status,
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "total_amount": order.total_amount,
        "total_price": order.total_price,
        "shipping_cost": order.shipping_cost,
        "created_at": order.created_at,
        "items": items_response,
    }
    # If the order was just marked as shipped or tracking info added, send notifications
    try:
        if ("status" in update_data and update_data.get("status") == "shipped") or ("tracking_number" in update_data and update_data.get("tracking_number")):
            order_dict_notify = {
                "id": order.id,
                "customer_name": order.customer_name,
                "customer_email": order.customer_email,
                "customer_phone": order.customer_phone,
                "total_amount": order.total_amount,
                "total_price": order.total_price,
                "payment_method": order.payment_method,
                "status": order.status,
                "tracking_number": order.tracking_number,
                "shipping_provider": order.shipping_provider,
            }
            # send shipment notification (best-effort)
            try:
                send_order_notification(order_dict_notify)  # notify admin
            except Exception:
                pass
            try:
                from app.services.email_service import send_shipment_notification
                send_shipment_notification(order_dict_notify)
            except Exception:
                pass
    except Exception:
        # don't fail the update because notification failed
        pass

    return order_response


# ===============================
# DELETE ORDER
# ===============================
@router.delete("/{order_id}", status_code=status.HTTP_200_OK)
def delete_order(order_id: int, session: Session = Depends(get_session)):
    """Delete an order and its associated items."""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Delete order items first
    order_items = session.exec(select(OrderItem).where(OrderItem.order_id == order_id)).all()
    for item in order_items:
        session.delete(item)

    session.delete(order)
    session.commit()
    return {"detail": f"Order ID {order_id} deleted successfully"}


# ===============================
# GENERATE OR DOWNLOAD INVOICE PDF FOR AN ORDER
# ===============================
@router.get("/{order_id}/invoice", response_class=FileResponse)
def get_order_invoice(order_id: int, session: Session = Depends(get_session)):
    """Generate or return an existing PDF invoice for the given order."""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Find associated invoice
    invoice = session.exec(select(Invoice).where(Invoice.order_id == order_id)).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="No invoice record found for this order")

    # Path where PDF should exist
    pdf_path = f"app/static/invoices/invoice_{invoice.id}.pdf"

    # Regenerate the PDF if missing
    if not os.path.exists(pdf_path):
        order_items = session.exec(select(OrderItem).where(OrderItem.order_id == order_id)).all()
        order_items_data = [
            {
                "name": session.get(Product, item.product_id).name,
                "quantity": item.quantity,
                "price": item.price,
            }
            for item in order_items
        ]

        invoice_data = {
            "invoice_id": invoice.id,
            "customer_name": order.customer_name,
            "customer_phone": order.customer_phone,
            "delivery_address": order.delivery_address,
            "order_items": order_items_data,
            "total_price": order.total_amount or order.total_price,
            "invoice_date": invoice.invoice_date,
        }

        pdf_path = generate_invoice_pdf(invoice_data)

    # Return the file for download
    return FileResponse(
        pdf_path,
        filename=f"invoice_{invoice.id}.pdf",
        media_type="application/pdf"
    )


# ===============================
# GENERATE RECEIPT PDF (for customers without email)
# ===============================
@router.get("/{order_id}/receipt", response_class=FileResponse)
def get_order_receipt(order_id: int, session: Session = Depends(get_session)):
    """Generate a receipt PDF for the given order (same as invoice but named receipt)."""
    # Reuse invoice generation
    return get_order_invoice(order_id, session)
