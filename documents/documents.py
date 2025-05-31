from flask import Blueprint, make_response, abort
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.pdf_generator import generate_pdf_from_template
from models import SalesReturn, SalesReturnItem, Customer, PurchaseInvoice, SalesInvoice, PurchaseReturn  # add missing models
from sqlalchemy.orm import joinedload

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')

@documents_bp.route('/sales-invoice/<int:invoice_id>/pdf')
def sales_invoice_pdf(invoice_id):
    invoice = SalesInvoice.query.options(
        joinedload(SalesInvoice.customer),
        joinedload(SalesInvoice.items)
    ).filter_by(id=invoice_id).first()
    if not invoice:
        abort(404, "Sales invoice not found.")
    context = {'invoice': invoice, 'company_logo': '/static/img/company_logo.png'}
    pdf = generate_pdf_from_template('pdf/sales_invoice.html', context)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=sales_invoice_{invoice.invoice_number}.pdf'
    return response

@documents_bp.route('/purchase-invoice/<int:invoice_id>/pdf')
def purchase_invoice_pdf(invoice_id):
    invoice = PurchaseInvoice.query.options(
        joinedload(PurchaseInvoice.supplier),
        joinedload(PurchaseInvoice.items)
    ).filter_by(id=invoice_id).first()
    if not invoice:
        abort(404, "Purchase invoice not found.")
    context = {'invoice': invoice, 'company_logo': '/static/img/company_logo.png'}
    pdf = generate_pdf_from_template('pdf/purchase_invoice.html', context)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=purchase_invoice_{invoice.invoice_number}.pdf'
    return response

@documents_bp.route('/sales-return/<int:return_id>/pdf')
def sales_return_pdf(return_id):
    sales_return = SalesReturn.query.options(
        joinedload(SalesReturn.customer),
        joinedload(SalesReturn.items)
    ).filter_by(id=return_id).first()
    if not sales_return:
        abort(404, "Sales return not found.")
    context = {'sales_return': sales_return, 'company_logo': '/static/img/company_logo.png'}
    pdf = generate_pdf_from_template('pdf/sales_return.html', context)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=sales_return_{sales_return.id}.pdf'
    return response

@documents_bp.route('/purchase-return/<int:return_id>/pdf')
def purchase_return_pdf(return_id):
    purchase_return = PurchaseReturn.query.options(
        joinedload(PurchaseReturn.supplier),
        joinedload(PurchaseReturn.items)
    ).filter_by(id=return_id).first()
    if not purchase_return:
        abort(404, "Purchase return not found.")
    context = {'purchase_return': purchase_return, 'company_logo': '/static/img/company_logo.png'}
    pdf = generate_pdf_from_template('pdf/purchase_return.html', context)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=purchase_return_{purchase_return.id}.pdf'
    return response

@documents_bp.route('/sales/bill/<string:invoice_number>')
def sales_bill_pdf(invoice_number):
    sales_invoice = SalesInvoice.query.options(
        joinedload(SalesInvoice.customer),
        joinedload(SalesInvoice.items)
    ).filter_by(invoice_number=invoice_number).first()
    if not sales_invoice:
        abort(404, "Sales invoice not found.")

    # Serve PDF from database if it exists
    if sales_invoice.bill_pdf:
        response = make_response(sales_invoice.bill_pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=sales_bill_{sales_invoice.invoice_number}.pdf'
        return response

    # If not present, generate PDF as fallback
    items = []
    for item in sales_invoice.items:
        items.append({
            'product_name': item.product.product_name,
            'quantity': item.quantity_sold,
            'unit_price': float(item.price_per_unit_before_gst),
            'subtotal': float(item.item_sub_total_before_gst)
        })

    bill = {
        'id': sales_invoice.invoice_number,
        'date': sales_invoice.invoice_date.strftime('%Y-%m-%d'),
        'customer_name': sales_invoice.customer.customer_name,
        'customer_address': sales_invoice.customer.billing_address_line1,
        'customer_contact': sales_invoice.customer.contact_number,
        'items': items,
        'subtotal': float(sales_invoice.total_amount_before_gst),
        'tax_rate': float(items[0]['unit_price'] if items else 0),  # Replace with GST % if needed
        'tax_amount': float(sales_invoice.total_gst_amount),
        'discount': float(sales_invoice.overall_discount_amount or 0),
        'total_amount': float(sales_invoice.total_invoice_amount),
        'payment_method': sales_invoice.payment_status,
        'logo_path': 'img/company_logo.png'
    }
    context = {
        'bill': bill,
        'title': 'Sales Bill',
        'bill_type_label': 'Bill To'
    }
    pdf = generate_pdf_from_template('bills/sales_bill_template.html', context)
    if pdf:
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=sales_bill_{sales_invoice.invoice_number}.pdf'
        return response
    abort(500, description="Error generating Sales Bill PDF")

@documents_bp.route('/purchases/bill/<string:invoice_number>')
def purchase_bill_pdf(invoice_number):
    purchase_invoice = PurchaseInvoice.query \
        .filter_by(invoice_number=invoice_number) \
        .first()
    if not purchase_invoice:
        abort(404, "Purchase bill not found.")

    items = []
    for item in purchase_invoice.items:
        items.append({
            'product_name': item.product.product_name,
            'quantity': item.quantity_purchased,
            'unit_price': float(item.price_per_unit_before_gst),
            'subtotal': float(item.item_sub_total_before_gst)
        })

    purchase_data = {
        'id': purchase_invoice.id,
        'date': purchase_invoice.invoice_date.strftime('%Y-%m-%d'),
        'supplier_name': purchase_invoice.supplier.supplier_name,
        'supplier_address': purchase_invoice.supplier.address_line1,
        'supplier_contact': purchase_invoice.supplier.supplier_contact,
        'items': items,
        'subtotal': float(purchase_invoice.total_amount_before_gst),
        'tax_rate': float(items[0]['unit_price'] if items else 0),  # Replace with GST % if needed
        'tax_amount': float(purchase_invoice.total_gst_amount),
        'discount': float(purchase_invoice.overall_discount_amount or 0),
        'total_amount': float(purchase_invoice.total_invoice_amount),
        'payment_method': purchase_invoice.payment_status,
        'logo_path': 'img/company_logo.png'
    }
    context = {
        'bill': purchase_data,
        'title': 'Purchase Bill',
        'bill_type_label': 'Bill From'
    }
    pdf = generate_pdf_from_template('bills/purchase_bill_template.html', context)
    if pdf:
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=purchase_bill_{purchase_invoice.invoice_number}.pdf'
        return response
    abort(500, description="Error generating Purchase Bill PDF")

@documents_bp.route('/sales_returns/bill/<string:return_number>')
def sales_return_bill_pdf(return_number):
    # Validate and extract the integer ID from "SR-<id>"
    if not return_number.startswith("SR-"):
        abort(404, "Invalid return number format.")
    try:
        return_id = int(return_number.replace("SR-", ""))
    except ValueError:
        abort(404, "Invalid return number format.")

    sales_return = SalesReturn.query.options(
        joinedload(SalesReturn.customer),
        joinedload(SalesReturn.items)
    ).filter_by(id=return_id).first()
    if not sales_return:
        abort(404, "Sales return not found.")

    items = []
    for item in sales_return.items:
        items.append({
            'product_name': item.product.product_name,
            'quantity': item.quantity_returned,
            'unit_price': float(item.price_per_unit_at_return),
            'subtotal': float(item.item_sub_total_before_gst)
        })

    bill = {
        'id': f"SR-{sales_return.id}",
        'reference_id': sales_return.original_invoice_id,
        'date': sales_return.return_date.strftime('%Y-%m-%d'),
        'customer_name': sales_return.customer.customer_name,
        'customer_address': sales_return.customer.billing_address_line1,
        'customer_contact': sales_return.customer.contact_number,
        'items': items,
        'subtotal': float(sales_return.total_items_value_before_gst),
        'tax_rate': float(items[0]['unit_price'] if items else 0),
        'tax_amount': float(sales_return.total_gst_reversed),
        'discount': 0,
        'total_amount': float(sales_return.final_amount_refunded),
        'payment_method': sales_return.mode_of_refund,
        'logo_path': 'img/company_logo.png'
    }

    context = {
        'bill': bill,
        'title': 'Sales Return Bill',
        'bill_type_label': 'Return To'
    }
    pdf = generate_pdf_from_template('bills/sales_return_bill_template.html', context)
    if pdf:
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=sales_return_bill_SR-{sales_return.id}.pdf'
        return response
    abort(500, description="Error generating Sales Return Bill PDF")

@documents_bp.route('/purchase_returns/bill/<string:return_number>')
def purchase_return_bill_pdf(return_number):
    # Validate and extract the integer ID from "PR-<id>"
    if not return_number.startswith("PR-"):
        abort(404, "Invalid return number format.")
    try:
        return_id = int(return_number.replace("PR-", ""))
    except ValueError:
        abort(404, "Invalid return number format.")

    purchase_return = PurchaseReturn.query.options(
        joinedload(PurchaseReturn.supplier),
        joinedload(PurchaseReturn.items)
    ).filter_by(id=return_id).first()
    if not purchase_return:
        abort(404, "Purchase return not found.")

    items = []
    for item in purchase_return.items:
        items.append({
            'product_name': item.product.product_name,
            'quantity': item.quantity_returned,
            'unit_price': float(item.price_per_unit_at_return),
            'subtotal': float(item.item_sub_total_before_gst)
        })

    bill = {
        'id': f"PR-{purchase_return.id}",
        'reference_id': purchase_return.original_purchase_invoice_id,
        'date': purchase_return.return_date.strftime('%Y-%m-%d'),
        'supplier_name': purchase_return.supplier.supplier_name,
        'supplier_address': purchase_return.supplier.address_line1,
        'supplier_contact': purchase_return.supplier.supplier_contact,
        'items': items,
        'subtotal': float(purchase_return.total_items_value_before_gst),
        'tax_rate': float(items[0]['unit_price'] if items else 0),  # Replace with GST % if needed
        'tax_amount': float(purchase_return.total_gst_claimed_back),
        'discount': 0,  # Add if you have a discount field
        'total_amount': float(purchase_return.final_amount_received),
        'payment_method': purchase_return.mode_of_refund_received,
        'logo_path': 'img/company_logo.png'
    }
    context = {
        'bill': bill,
        'title': 'Purchase Return Bill',
        'bill_type_label': 'Return From'
    }
    pdf = generate_pdf_from_template('bills/purchase_return_bill_template.html', context)
    if pdf:
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=purchase_return_bill_PR-{purchase_return.id}.pdf'
        return response
    abort(500, description="Error generating Purchase Return Bill PDF")