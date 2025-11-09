# app/utils/pdf_generator.py
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_invoice_pdf(invoice_data: dict, output_dir: str = "app/static/invoices") -> str:
    """
    Generate an invoice PDF and return its file path.
    invoice_data should include:
    - invoice_id
    - customer_name
    - customer_phone
    - delivery_address
    - order_items (list of dicts: {name, quantity, price})
    - total_price
    - invoice_date
    """

    os.makedirs(output_dir, exist_ok=True)
    filename = f"invoice_{invoice_data['invoice_id']}.pdf"
    file_path = os.path.join(output_dir, filename)

    # Set up PDF document
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Header section
    title = Paragraph("<b>Morine Gypsum</b>", styles["Title"])
    subtitle = Paragraph(f"<b>Invoice ID:</b> #{invoice_data['invoice_id']}", styles["Heading2"])
    date_str = invoice_data["invoice_date"].strftime("%Y-%m-%d %H:%M")
    elements.extend([title, subtitle, Paragraph(f"Date: {date_str}", styles["Normal"]), Spacer(1, 12)])

    # Customer Info
    elements.append(Paragraph("<b>Customer Information</b>", styles["Heading3"]))
    elements.append(Paragraph(f"Name: {invoice_data['customer_name']}", styles["Normal"]))
    elements.append(Paragraph(f"Phone: {invoice_data['customer_phone']}", styles["Normal"]))
    elements.append(Paragraph(f"Address: {invoice_data['delivery_address']}", styles["Normal"]))
    elements.append(Spacer(1, 10))

    # Order Items Table
    table_data = [["Product", "Quantity", "Price (KES)", "Total (KES)"]]
    for item in invoice_data["order_items"]:
        total = item["quantity"] * item["price"]
        table_data.append([
            item["name"],
            str(item["quantity"]),
            f"{item['price']:.2f}",
            f"{total:.2f}"
        ])

    # Add total row
    table_data.append(["", "", "<b>Total:</b>", f"<b>{invoice_data['total_price']:.2f}</b>"])

    # Table design
    table = Table(table_data, colWidths=[70*mm, 30*mm, 35*mm, 35*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E8B57")),  # header
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 1), (-1, -2), colors.whitesmoke),
        ("BACKGROUND", (-2, -1), (-1, -1), colors.beige),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 15))

    # Footer / Remarks
    elements.append(Paragraph("<b>Remarks:</b> Payment due upon delivery.", styles["Normal"]))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<i>Thank you for choosing Morine Gypsum!</i>", styles["Italic"]))

    # Build PDF
    doc.build(elements)
    return file_path
