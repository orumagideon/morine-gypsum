# app/routers/order_router.py
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlmodel import select, Session
from app.db.session import get_session
from app.models.models import Order, OrderItem, Product, Invoice
from app.schemas.schemas import OrderCreate, OrderRead, OrderUpdate
from app.utils.pdf_generator import generate_invoice_pdf

router = APIRouter(prefix="/orders", tags=["Orders"])


# ===============================
# CREATE ORDER (with invoice generation)
# ===============================
@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate, session: Session = Depends(get_session)):
    """Create an order, generate invoice, and return details."""
    if not order_data.items:
        raise HTTPException(status_code=400, detail="Order must have at least one product")

    # Initialize order
    order = Order(
        customer_name=order_data.customer_name,
        customer_phone=order_data.customer_phone,
        delivery_address=order_data.delivery_address,
        status="Pending",
        created_at=datetime.utcnow(),
        total_price=0.0
    )
    session.add(order)
    session.commit()
    session.refresh(order)

    total_order_price = 0.0
    order_items = []

    # Process each product
    for item in order_data.items:
        product = session.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product ID {item.product_id} not found")

        if product.stock_quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")

        total_price = product.price * item.quantity
        total_order_price += total_price

        # Update product stock
        product.stock_quantity -= item.quantity
        session.add(product)

        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price
        )
        session.add(order_item)
        order_items.append(order_item)

    # Update total order price
    order.total_price = total_order_price
    session.add(order)
    session.commit()
    session.refresh(order)

    # ===============================
    # Create Invoice Record
    # ===============================
    new_invoice = Invoice(
        order_id=order.id,
        total_amount=total_order_price,
        payment_method="Cash",
        payment_status="Pending",
        invoice_date=datetime.utcnow()
    )
    session.add(new_invoice)
    session.commit()
    session.refresh(new_invoice)

    # ===============================
    # Generate PDF Invoice
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
        "total_price": total_order_price,
        "invoice_date": new_invoice.invoice_date,
    }

    pdf_path = generate_invoice_pdf(invoice_data)
    new_invoice.remarks = f"PDF generated at: {pdf_path}"
    session.add(new_invoice)
    session.commit()

    return order


# ===============================
# READ ALL ORDERS
# ===============================
@router.get("/", response_model=list[OrderRead])
def get_orders(session: Session = Depends(get_session)):
    orders = session.exec(select(Order)).all()
    return orders


# ===============================
# READ SINGLE ORDER
# ===============================
@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# ===============================
# UPDATE ORDER STATUS
# ===============================
@router.put("/{order_id}", response_model=OrderRead)
def update_order(order_id: int, order_update: OrderUpdate, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order_update.status:
        order.status = order_update.status

    session.add(order)
    session.commit()
    session.refresh(order)
    return order


# ===============================
# DELETE ORDER
# ===============================
@router.delete("/{order_id}", status_code=status.HTTP_200_OK)
def delete_order(order_id: int, session: Session = Depends(get_session)):
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
# DOWNLOAD INVOICE PDF
# ===============================
@router.get("/invoice/{invoice_id}/download", response_class=FileResponse)
def download_invoice(invoice_id: int):
    """Download generated invoice as a PDF file."""
    file_path = f"app/static/invoices/invoice_{invoice_id}.pdf"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Invoice PDF not found")

    return FileResponse(
        file_path,
        filename=f"invoice_{invoice_id}.pdf",
        media_type="application/pdf"
    )
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
            "total_price": order.total_price,
            "invoice_date": invoice.invoice_date,
        }

        from app.utils.pdf_generator import generate_invoice_pdf
        pdf_path = generate_invoice_pdf(invoice_data)

    # Return the file for download
    return FileResponse(
        pdf_path,
        filename=f"invoice_{invoice.id}.pdf",
        media_type="application/pdf"
    )
