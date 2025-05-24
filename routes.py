# routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
import uuid
from models import db, Product, Customer, User, SalesInvoice, SalesInvoiceItem, PurchaseInvoice, PurchaseInvoiceItem, SalesReturn, SalesReturnItem, PurchaseReturn, PurchaseReturnItem, Supplier # Add Supplier here

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html') # Assumes index.html exists

# --- Product CRUD ---
@main.route('/products')
def product_list():
    products = Product.query.all()
    return render_template('view_products.html', products=products)

@main.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product = Product(
            product_name=request.form['product_name'],
            product_code=request.form['product_code'],
            hsn_code=request.form.get('hsn_code'),
            measuring_units=request.form.get('measuring_units'),
            reorder_level=request.form.get('reorder_level', 0),
            gst_available=request.form.get('gst_available', 'no'),
            gst_percentage=request.form.get('gst_percentage', 0.0),
            description=request.form.get('description'),
            current_stock=request.form.get('current_stock', 0)
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('main.product_list'))
    return render_template('new_product_form.html')

@main.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.product_name = request.form['product_name']
        product.product_code = request.form['product_code']
        product.hsn_code = request.form.get('hsn_code')
        product.measuring_units = request.form.get('measuring_units')
        product.reorder_level = request.form.get('reorder_level', 0)
        product.gst_available = request.form.get('gst_available', 'no')
        product.gst_percentage = request.form.get('gst_percentage', 0.0)
        product.description = request.form.get('description')
        product.current_stock = request.form.get('current_stock', 0)
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('main.product_list'))
    return render_template('new_product_form.html', product=product)

@main.route('/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('main.product_list'))

# --- Customer CRUD ---
@main.route('/customers')
def customer_list():
    customers = Customer.query.all()
    return render_template('view_customers.html', customers=customers)

@main.route('/customers/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        customer = Customer(
            customer_name=request.form['customer_name'],
            contact_number=request.form.get('contact_number'),
            email_address=request.form.get('email_address'),
            billing_address_line1=request.form.get('billing_address_line1'),
            billing_pincode=request.form.get('billing_pincode'),
            billing_city=request.form.get('billing_city'),
            billing_state=request.form.get('billing_state'),
            billing_country=request.form.get('billing_country', 'India'),
            shipping_address_line1=request.form.get('shipping_address_line1'),
            shipping_pincode=request.form.get('shipping_pincode'),
            shipping_city=request.form.get('shipping_city'),
            shipping_state=request.form.get('shipping_state'),
            shipping_country=request.form.get('shipping_country', 'India'),
            description=request.form.get('description')
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer added successfully!', 'success')
        return redirect(url_for('main.customer_list'))
    return render_template('new_customer_form.html')

@main.route('/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if request.method == 'POST':
        customer.customer_name = request.form['customer_name']
        customer.contact_number = request.form.get('contact_number')
        customer.email_address = request.form.get('email_address')
        customer.billing_address_line1 = request.form.get('billing_address_line1')
        customer.billing_pincode = request.form.get('billing_pincode')
        customer.billing_city = request.form.get('billing_city')
        customer.billing_state = request.form.get('billing_state')
        customer.billing_country = request.form.get('billing_country', 'India')
        customer.shipping_address_line1 = request.form.get('shipping_address_line1')
        customer.shipping_pincode = request.form.get('shipping_pincode')
        customer.shipping_city = request.form.get('shipping_city')
        customer.shipping_state = request.form.get('shipping_state')
        customer.shipping_country = request.form.get('shipping_country', 'India')
        customer.description = request.form.get('description')
        db.session.commit()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('main.customer_list'))
    return render_template('new_customer_form.html', customer=customer)

@main.route('/customers/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    # Prevent deletion if customer has related sales invoices or sales returns
    if customer.sales_invoices or customer.sales_returns:
        flash('Cannot delete customer: there are related sales invoices or sales returns.', 'danger')
        return redirect(url_for('main.customer_list'))
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted successfully!', 'success')
    return redirect(url_for('main.customer_list'))

# --- Supplier CRUD ---
@main.route('/suppliers')
def supplier_list():
    suppliers = Supplier.query.all()
    return render_template('view_suppliers.html', suppliers=suppliers)

@main.route('/suppliers/add', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        supplier = Supplier(
            supplier_name=request.form['supplier_name'],
            supplier_contact=request.form.get('supplier_contact'),
            gst_available=request.form.get('gst_available', 'no'),
            gst_number=request.form.get('gst_number'),
            address_line1=request.form.get('address_line1'),
            address_pincode=request.form.get('address_pincode'),
            address_city=request.form.get('address_city'),
            address_state=request.form.get('address_state'),
            address_country=request.form.get('address_country', 'India'),
            account_available=request.form.get('account_available', 'no'),
            account_holder_name=request.form.get('account_holder_name'),
            account_number=request.form.get('account_number'),
            ifsc_code=request.form.get('ifsc_code'),
            branch=request.form.get('branch')
        )
        db.session.add(supplier)
        db.session.commit()
        flash('Supplier added successfully!', 'success')
        return redirect(url_for('main.supplier_list'))
    return render_template('supplier_form.html')

@main.route('/suppliers/edit/<int:supplier_id>', methods=['GET', 'POST'])
def edit_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    if request.method == 'POST':
        supplier.supplier_name = request.form['supplier_name']
        supplier.supplier_contact = request.form.get('supplier_contact')
        supplier.gst_available = request.form.get('gst_available', 'no')
        supplier.gst_number = request.form.get('gst_number')
        supplier.address_line1 = request.form.get('address_line1')
        supplier.address_pincode = request.form.get('address_pincode')
        supplier.address_city = request.form.get('address_city')
        supplier.address_state = request.form.get('address_state')
        supplier.address_country = request.form.get('address_country', 'India')
        supplier.account_available = request.form.get('account_available', 'no')
        supplier.account_holder_name = request.form.get('account_holder_name')
        supplier.account_number = request.form.get('account_number')
        supplier.ifsc_code = request.form.get('ifsc_code')
        supplier.branch = request.form.get('branch')
        db.session.commit()
        flash('Supplier updated successfully!', 'success')
        return redirect(url_for('main.supplier_list'))
    return render_template('supplier_form.html', supplier=supplier)

@main.route('/suppliers/delete/<int:supplier_id>', methods=['POST'])
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    db.session.delete(supplier)
    db.session.commit()
    flash('Supplier deleted successfully!', 'success')
    return redirect(url_for('main.supplier_list'))

# --- SalesInvoice CRUD ---
@main.route('/sales-invoices')
def sales_invoice_list():
    return redirect(url_for('main.sales_transactions'))

@main.route('/sales-invoices/add', methods=['GET', 'POST'])
def add_sales_invoice():
    if request.method == 'POST':
        sales_invoice = SalesInvoice(
            invoice_number=request.form['invoice_number'],
            invoice_date=request.form['invoice_date'],
            customer_id=request.form['customer_id'],
            executive_id=request.form.get('executive_id'),
            total_amount_before_gst=request.form.get('total_amount_before_gst', 0.0),
            total_gst_amount=request.form.get('total_gst_amount', 0.0),
            overall_discount_amount=request.form.get('overall_discount_amount', 0.0),
            total_invoice_amount=request.form.get('total_invoice_amount', 0.0),
            payment_status=request.form.get('payment_status', 'Pending'),
            notes=request.form.get('notes')
        )
        db.session.add(sales_invoice)
        db.session.commit()
        flash('Sales invoice added successfully!', 'success')
        return redirect(url_for('main.sales_invoice_list'))
    return render_template('sales_invoices/add.html')

@main.route('/sales-invoices/edit/<int:invoice_id>', methods=['GET', 'POST'])
def edit_sales_invoice(invoice_id):
    sales_invoice = SalesInvoice.query.get_or_404(invoice_id)
    if request.method == 'POST':
        sales_invoice.invoice_number = request.form['invoice_number']
        sales_invoice.invoice_date = request.form['invoice_date']
        sales_invoice.customer_id = request.form['customer_id']
        sales_invoice.executive_id = request.form.get('executive_id')
        sales_invoice.total_amount_before_gst = request.form.get('total_amount_before_gst', 0.0)
        sales_invoice.total_gst_amount = request.form.get('total_gst_amount', 0.0)
        sales_invoice.overall_discount_amount = request.form.get('overall_discount_amount', 0.0)
        sales_invoice.total_invoice_amount = request.form.get('total_invoice_amount', 0.0)
        sales_invoice.payment_status = request.form.get('payment_status', 'Pending')
        sales_invoice.notes = request.form.get('notes')
        db.session.commit()
        flash('Sales invoice updated successfully!', 'success')
        return redirect(url_for('main.sales_invoice_list'))
    return render_template('sales_invoices/add.html', sales_invoice=sales_invoice)

@main.route('/sales-invoices/delete/<int:invoice_id>', methods=['POST'])
def delete_sales_invoice(invoice_id):
    sales_invoice = SalesInvoice.query.get_or_404(invoice_id)
    db.session.delete(sales_invoice)
    db.session.commit()
    flash('Sales invoice deleted successfully!', 'success')
    return redirect(url_for('main.sales_invoice_list'))

# --- PurchaseInvoice CRUD ---
@main.route('/purchase-invoices')
def purchase_invoice_list():
    return redirect(url_for('main.purchase_transactions'))

@main.route('/purchase-invoices/add', methods=['GET', 'POST'])
def add_purchase_invoice():
    if request.method == 'POST':
        purchase_invoice = PurchaseInvoice(
            invoice_number=request.form['invoice_number'],
            invoice_date=request.form['invoice_date'],
            supplier_id=request.form['supplier_id'],
            total_amount_before_gst=request.form.get('total_amount_before_gst', 0.0),
            total_gst_amount=request.form.get('total_gst_amount', 0.0),
            overall_discount_amount=request.form.get('overall_discount_amount', 0.0),
            total_invoice_amount=request.form.get('total_invoice_amount', 0.0),
            payment_status=request.form.get('payment_status', 'Pending'),
            bill_copy_path=request.form.get('bill_copy_path'),
            notes=request.form.get('notes')
        )
        db.session.add(purchase_invoice)
        db.session.commit()
        flash('Purchase invoice added successfully!', 'success')
        return redirect(url_for('main.purchase_invoice_list'))
    return render_template('purchase_invoices/add.html')

@main.route('/purchase-invoices/edit/<int:invoice_id>', methods=['GET', 'POST'])
def edit_purchase_invoice(invoice_id):
    purchase_invoice = PurchaseInvoice.query.get_or_404(invoice_id)
    if request.method == 'POST':
        purchase_invoice.invoice_number = request.form['invoice_number']
        purchase_invoice.invoice_date = request.form['invoice_date']
        purchase_invoice.supplier_id = request.form['supplier_id']
        purchase_invoice.total_amount_before_gst = request.form.get('total_amount_before_gst', 0.0)
        purchase_invoice.total_gst_amount = request.form.get('total_gst_amount', 0.0)
        purchase_invoice.overall_discount_amount = request.form.get('overall_discount_amount', 0.0)
        purchase_invoice.total_invoice_amount = request.form.get('total_invoice_amount', 0.0)
        purchase_invoice.payment_status = request.form.get('payment_status', 'Pending')
        purchase_invoice.bill_copy_path = request.form.get('bill_copy_path')
        purchase_invoice.notes = request.form.get('notes')
        db.session.commit()
        flash('Purchase invoice updated successfully!', 'success')
        return redirect(url_for('main.purchase_invoice_list'))
    return render_template('purchase_invoices/add.html', purchase_invoice=purchase_invoice)

@main.route('/purchase-invoices/delete/<int:invoice_id>', methods=['POST'])
def delete_purchase_invoice(invoice_id):
    purchase_invoice = PurchaseInvoice.query.get_or_404(invoice_id)
    db.session.delete(purchase_invoice)
    db.session.commit()
    flash('Purchase invoice deleted successfully!', 'success')
    return redirect(url_for('main.purchase_invoice_list'))

# --- SalesReturn CRUD ---
@main.route('/sales-returns')
def sales_return_list():
    sales_returns = SalesReturn.query.all()
    return render_template('sales_returns/list.html', sales_returns=sales_returns)

@main.route('/sales-returns/add', methods=['GET', 'POST'])
def add_sales_return():
    if request.method == 'POST':
        sales_return = SalesReturn(
            return_date=request.form['return_date'],
            original_invoice_id=request.form['original_invoice_id'],
            customer_id=request.form['customer_id'],
            executive_id=request.form.get('executive_id'),
            return_reason=request.form.get('return_reason'),
            total_items_value_before_gst=request.form.get('total_items_value_before_gst', 0.0),
            total_gst_reversed=request.form.get('total_gst_reversed', 0.0),
            net_refundable_amount=request.form.get('net_refundable_amount', 0.0),
            mode_of_refund=request.form.get('mode_of_refund'),
            refund_option=request.form.get('refund_option', 'full-refund'),
            partial_refund_amount_input=request.form.get('partial_refund_amount_input'),
            final_amount_refunded=request.form.get('final_amount_refunded', 0.0),
            notes=request.form.get('notes')
        )
        db.session.add(sales_return)
        db.session.commit()
        flash('Sales return added successfully!', 'success')
        return redirect(url_for('main.sales_return_list'))
    return render_template('sales_returns/add.html')

@main.route('/sales-returns/edit/<int:return_id>', methods=['GET', 'POST'])
def edit_sales_return(return_id):
    sales_return = SalesReturn.query.get_or_404(return_id)
    if request.method == 'POST':
        sales_return.return_date = request.form['return_date']
        sales_return.original_invoice_id = request.form['original_invoice_id']
        sales_return.customer_id = request.form['customer_id']
        sales_return.executive_id = request.form.get('executive_id')
        sales_return.return_reason = request.form.get('return_reason')
        sales_return.total_items_value_before_gst = request.form.get('total_items_value_before_gst', 0.0)
        sales_return.total_gst_reversed = request.form.get('total_gst_reversed', 0.0)
        sales_return.net_refundable_amount = request.form.get('net_refundable_amount', 0.0)
        sales_return.mode_of_refund = request.form.get('mode_of_refund')
        sales_return.refund_option = request.form.get('refund_option', 'full-refund')
        sales_return.partial_refund_amount_input = request.form.get('partial_refund_amount_input')
        sales_return.final_amount_refunded = request.form.get('final_amount_refunded', 0.0)
        sales_return.notes = request.form.get('notes')
        db.session.commit()
        flash('Sales return updated successfully!', 'success')
        return redirect(url_for('main.sales_return_list'))
    return render_template('sales_returns/add.html', sales_return=sales_return)

@main.route('/sales-returns/delete/<int:return_id>', methods=['POST'])
def delete_sales_return(return_id):
    sales_return = SalesReturn.query.get_or_404(return_id)
    db.session.delete(sales_return)
    db.session.commit()
    flash('Sales return deleted successfully!', 'success')
    return redirect(url_for('main.sales_return_list'))

# --- PurchaseReturn CRUD ---
@main.route('/purchase-returns')
def purchase_return_list():
    purchase_returns = PurchaseReturn.query.all()
    return render_template('purchase_returns/list.html', purchase_returns=purchase_returns)

@main.route('/purchase-returns/add', methods=['GET', 'POST'])
def add_purchase_return():
    if request.method == 'POST':
        purchase_return = PurchaseReturn(
            return_date=request.form['return_date'],
            original_purchase_invoice_id=request.form['original_purchase_invoice_id'],
            supplier_id=request.form['supplier_id'],
            return_reason=request.form.get('return_reason'),
            total_items_value_before_gst=request.form.get('total_items_value_before_gst', 0.0),
            total_gst_claimed_back=request.form.get('total_gst_claimed_back', 0.0),
            net_amount_receivable=request.form.get('net_amount_receivable', 0.0),
            mode_of_refund_received=request.form.get('mode_of_refund_received'),
            refund_receipt_option=request.form.get('refund_receipt_option', 'full-amount'),
            partial_amount_received_input=request.form.get('partial_amount_received_input'),
            final_amount_received=request.form.get('final_amount_received', 0.0),
            notes=request.form.get('notes')
        )
        db.session.add(purchase_return)
        db.session.commit()
        flash('Purchase return added successfully!', 'success')
        return redirect(url_for('main.purchase_return_list'))
    return render_template('purchase_returns/add.html')

@main.route('/purchase-returns/edit/<int:return_id>', methods=['GET', 'POST'])
def edit_purchase_return(return_id):
    purchase_return = PurchaseReturn.query.get_or_404(return_id)
    if request.method == 'POST':
        purchase_return.return_date = request.form['return_date']
        purchase_return.original_purchase_invoice_id = request.form['original_purchase_invoice_id']
        purchase_return.supplier_id = request.form['supplier_id']
        purchase_return.return_reason = request.form.get('return_reason')
        purchase_return.total_items_value_before_gst = request.form.get('total_items_value_before_gst', 0.0)
        purchase_return.total_gst_claimed_back = request.form.get('total_gst_claimed_back', 0.0)
        purchase_return.net_amount_receivable = request.form.get('net_amount_receivable', 0.0)
        purchase_return.mode_of_refund_received = request.form.get('mode_of_refund_received')
        purchase_return.refund_receipt_option = request.form.get('refund_receipt_option', 'full-amount')
        purchase_return.partial_amount_received_input = request.form.get('partial_amount_received_input')
        purchase_return.final_amount_received = request.form.get('final_amount_received', 0.0)
        purchase_return.notes = request.form.get('notes')
        db.session.commit()
        flash('Purchase return updated successfully!', 'success')
        return redirect(url_for('main.purchase_return_list'))
    return render_template('purchase_returns/add.html', purchase_return=purchase_return)

@main.route('/purchase-returns/delete/<int:return_id>', methods=['POST'])
def delete_purchase_return(return_id):
    purchase_return = PurchaseReturn.query.get_or_404(return_id)
    db.session.delete(purchase_return)
    db.session.commit()
    flash('Purchase return deleted successfully!', 'success')
    return redirect(url_for('main.purchase_return_list'))

# --- User CRUD ---
@main.route('/users')
def user_list():
    users = User.query.all()
    return render_template('users/list.html', users=users)

@main.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        user = User(
            full_name=request.form['full_name'],
            email=request.form['email'],
            role=request.form.get('role'),
            is_active=bool(request.form.get('is_active', True)),
            password_hash=request.form.get('password_hash')
        )
        db.session.add(user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('main.user_list'))
    return render_template('users/add.html')

@main.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.full_name = request.form['full_name']
        user.email = request.form['email']
        user.role = request.form.get('role')
        user.is_active = bool(request.form.get('is_active', True))
        user.password_hash = request.form.get('password_hash')
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('main.user_list'))
    return render_template('users/add.html', user=user)

@main.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('main.user_list'))

# --- API Endpoints ---
@main.route('/api/products')
def api_products():
    products = Product.query.all()
    return jsonify([
        {
            'product_id': p.id,
            'product_name': p.product_name,
            'product_code': p.product_code,
            'price_per_unit': None,  # Add price if you have it in your schema
            'gst_percentage': float(p.gst_percentage) if p.gst_percentage else 0.0
        } for p in products
    ])

@main.route('/api/customers')
def api_customers():
    customers = Customer.query.all()
    return jsonify([
        {
            'customer_id': c.id,
            'customer_name': c.customer_name
        } for c in customers
    ])

@main.route('/api/executives')
def api_executives():
    executives = User.query.all()  # Fetch all users, not just executives
    return jsonify([
        {
            'executive_id': e.id,
            'full_name': e.full_name
        } for e in executives
    ])

@main.route('/sales-entry')
def sales_entry():
    return render_template('sales_entry.html')

@main.route('/purchase-form')
def purchases_form():
    return render_template('purchase_form.html')

@main.route('/sales-return')
def sales_return():
    return render_template('sales_return.html')

@main.route('/purchase-return')
def purchase_return():
    return render_template('purchase_return_form.html')

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# --- SalesInvoiceItem CRUD ---
@main.route('/sales-invoice/<int:invoice_id>/items')
def sales_invoice_items(invoice_id):
    items = SalesInvoiceItem.query.filter_by(sales_invoice_id=invoice_id).all()
    return render_template('sales_invoices/items.html', items=items, invoice_id=invoice_id)

@main.route('/sales-invoice/<int:invoice_id>/items/add', methods=['GET', 'POST'])
def add_sales_invoice_item(invoice_id):
    if request.method == 'POST':
        item = SalesInvoiceItem(
            sales_invoice_id=invoice_id,
            product_id=request.form['product_id'],
            quantity_sold=request.form['quantity_sold'],
            price_per_unit_before_gst=request.form['price_per_unit_before_gst'],
            gst_percentage=request.form.get('gst_percentage', 0.0),
            gst_amount_per_unit=request.form.get('gst_amount_per_unit', 0.0),
            item_discount_amount=request.form.get('item_discount_amount', 0.0),
            item_sub_total_before_gst=request.form['item_sub_total_before_gst'],
            item_total_gst_amount=request.form['item_total_gst_amount'],
            item_final_amount=request.form['item_final_amount']
        )
        db.session.add(item)
        db.session.commit()
        flash('Sales invoice item added!', 'success')
        return redirect(url_for('main.sales_invoice_items', invoice_id=invoice_id))
    return render_template('sales_invoices/add_item.html', invoice_id=invoice_id)

@main.route('/sales-invoice/items/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_sales_invoice_item(item_id):
    item = SalesInvoiceItem.query.get_or_404(item_id)
    if request.method == 'POST':
        item.product_id = request.form['product_id']
        item.quantity_sold = request.form['quantity_sold']
        item.price_per_unit_before_gst = request.form['price_per_unit_before_gst']
        item.gst_percentage = request.form.get('gst_percentage', 0.0)
        item.gst_amount_per_unit = request.form.get('gst_amount_per_unit', 0.0)
        item.item_discount_amount = request.form.get('item_discount_amount', 0.0)
        item.item_sub_total_before_gst = request.form['item_sub_total_before_gst']
        item.item_total_gst_amount = request.form['item_total_gst_amount']
        item.item_final_amount = request.form['item_final_amount']
        db.session.commit()
        flash('Sales invoice item updated!', 'success')
        return redirect(url_for('main.sales_invoice_items', invoice_id=item.sales_invoice_id))
    return render_template('sales_invoices/add_item.html', item=item, invoice_id=item.sales_invoice_id)

@main.route('/sales-invoice/items/delete/<int:item_id>', methods=['POST'])
def delete_sales_invoice_item(item_id):
    item = SalesInvoiceItem.query.get_or_404(item_id)
    invoice_id = item.sales_invoice_id
    db.session.delete(item)
    db.session.commit()
    flash('Sales invoice item deleted!', 'success')
    return redirect(url_for('main.sales_invoice_items', invoice_id=invoice_id))

# --- PurchaseInvoiceItem CRUD ---
@main.route('/purchase-invoice/<int:invoice_id>/items')
def purchase_invoice_items(invoice_id):
    items = PurchaseInvoiceItem.query.filter_by(purchase_invoice_id=invoice_id).all()
    return render_template('purchase_invoices/items.html', items=items, invoice_id=invoice_id)

@main.route('/purchase-invoice/<int:invoice_id>/items/add', methods=['GET', 'POST'])
def add_purchase_invoice_item(invoice_id):
    if request.method == 'POST':
        item = PurchaseInvoiceItem(
            purchase_invoice_id=invoice_id,
            product_id=request.form['product_id'],
            quantity_purchased=request.form['quantity_purchased'],
            price_per_unit_before_gst=request.form['price_per_unit_before_gst'],
            gst_percentage=request.form.get('gst_percentage', 0.0),
            gst_amount_per_unit=request.form.get('gst_amount_per_unit', 0.0),
            item_discount_amount=request.form.get('item_discount_amount', 0.0),
            item_sub_total_before_gst=request.form['item_sub_total_before_gst'],
            item_total_gst_amount=request.form['item_total_gst_amount'],
            item_final_amount=request.form['item_final_amount']
        )
        db.session.add(item)
        db.session.commit()
        flash('Purchase invoice item added!', 'success')
        return redirect(url_for('main.purchase_invoice_items', invoice_id=invoice_id))
    return render_template('purchase_invoices/add_item.html', invoice_id=invoice_id)

@main.route('/purchase-invoice/items/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_purchase_invoice_item(item_id):
    item = PurchaseInvoiceItem.query.get_or_404(item_id)
    if request.method == 'POST':
        item.product_id = request.form['product_id']
        item.quantity_purchased = request.form['quantity_purchased']
        item.price_per_unit_before_gst = request.form['price_per_unit_before_gst']
        item.gst_percentage = request.form.get('gst_percentage', 0.0)
        item.gst_amount_per_unit = request.form.get('gst_amount_per_unit', 0.0)
        item.item_discount_amount = request.form.get('item_discount_amount', 0.0)
        item.item_sub_total_before_gst = request.form['item_sub_total_before_gst']
        item.item_total_gst_amount = request.form['item_total_gst_amount']
        item.item_final_amount = request.form['item_final_amount']
        db.session.commit()
        flash('Purchase invoice item updated!', 'success')
        return redirect(url_for('main.purchase_invoice_items', invoice_id=item.purchase_invoice_id))
    return render_template('purchase_invoices/add_item.html', item=item, invoice_id=item.purchase_invoice_id)

@main.route('/purchase-invoice/items/delete/<int:item_id>', methods=['POST'])
def delete_purchase_invoice_item(item_id):
    item = PurchaseInvoiceItem.query.get_or_404(item_id)
    invoice_id = item.purchase_invoice_id
    db.session.delete(item)
    db.session.commit()
    flash('Purchase invoice item deleted!', 'success')
    return redirect(url_for('main.purchase_invoice_items', invoice_id=invoice_id))

# --- SalesReturnItem CRUD ---
@main.route('/sales-return/<int:return_id>/items')
def sales_return_items(return_id):
    items = SalesReturnItem.query.filter_by(sales_return_id=return_id).all()
    return render_template('sales_returns/items.html', items=items, return_id=return_id)

@main.route('/sales-return/<int:return_id>/items/add', methods=['GET', 'POST'])
def add_sales_return_item(return_id):
    if request.method == 'POST':
        item = SalesReturnItem(
            sales_return_id=return_id,
            product_id=request.form['product_id'],
            original_sales_invoice_item_id=request.form.get('original_sales_invoice_item_id'),
            quantity_returned=request.form['quantity_returned'],
            price_per_unit_at_return=request.form['price_per_unit_at_return'],
            gst_percentage_applied=request.form.get('gst_percentage_applied', 0.0),
            gst_amount_reversed_per_unit=request.form.get('gst_amount_reversed_per_unit', 0.0),
            item_sub_total_before_gst=request.form['item_sub_total_before_gst'],
            item_total_gst_reversed=request.form['item_total_gst_reversed'],
            item_final_value=request.form['item_final_value']
        )
        db.session.add(item)
        db.session.commit()
        flash('Sales return item added!', 'success')
        return redirect(url_for('main.sales_return_items', return_id=return_id))
    return render_template('sales_returns/add_item.html', return_id=return_id)

@main.route('/sales-return/items/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_sales_return_item(item_id):
    item = SalesReturnItem.query.get_or_404(item_id)
    if request.method == 'POST':
        item.product_id = request.form['product_id']
        item.original_sales_invoice_item_id = request.form.get('original_sales_invoice_item_id')
        item.quantity_returned = request.form['quantity_returned']
        item.price_per_unit_at_return = request.form['price_per_unit_at_return']
        item.gst_percentage_applied = request.form.get('gst_percentage_applied', 0.0)
        item.gst_amount_reversed_per_unit = request.form.get('gst_amount_reversed_per_unit', 0.0)
        item.item_sub_total_before_gst = request.form['item_sub_total_before_gst']
        item.item_total_gst_reversed = request.form['item_total_gst_reversed']
        item.item_final_value = request.form['item_final_value']
        db.session.commit()
        flash('Sales return item updated!', 'success')
        return redirect(url_for('main.sales_return_items', return_id=item.sales_return_id))
    return render_template('sales_returns/add_item.html', item=item, return_id=item.sales_return_id)

@main.route('/sales-return/items/delete/<int:item_id>', methods=['POST'])
def delete_sales_return_item(item_id):
    item = SalesReturnItem.query.get_or_404(item_id)
    return_id = item.sales_return_id
    db.session.delete(item)
    db.session.commit()
    flash('Sales return item deleted!', 'success')
    return redirect(url_for('main.sales_return_items', return_id=return_id))

# --- PurchaseReturnItem CRUD ---
@main.route('/purchase-return/<int:return_id>/items')
def purchase_return_items(return_id):
    items = PurchaseReturnItem.query.filter_by(purchase_return_id=return_id).all()
    return render_template('purchase_returns/items.html', items=items, return_id=return_id)

@main.route('/purchase-return/<int:return_id>/items/add', methods=['GET', 'POST'])
def add_purchase_return_item(return_id):
    if request.method == 'POST':
        item = PurchaseReturnItem(
            purchase_return_id=return_id,
            product_id=request.form['product_id'],
            original_purchase_invoice_item_id=request.form.get('original_purchase_invoice_item_id'),
            quantity_returned=request.form['quantity_returned'],
            price_per_unit_at_return=request.form['price_per_unit_at_return'],
            gst_percentage_applied=request.form.get('gst_percentage_applied', 0.0),
            gst_amount_claimed_back_per_unit=request.form.get('gst_amount_claimed_back_per_unit', 0.0),
            item_sub_total_before_gst=request.form['item_sub_total_before_gst'],
            item_total_gst_claimed_back=request.form['item_total_gst_claimed_back'],
            item_final_value=request.form['item_final_value']
        )
        db.session.add(item)
        db.session.commit()
        flash('Purchase return item added!', 'success')
        return redirect(url_for('main.purchase_return_items', return_id=return_id))
    return render_template('purchase_returns/add_item.html', return_id=return_id)

@main.route('/purchase-return/items/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_purchase_return_item(item_id):
    item = PurchaseReturnItem.query.get_or_404(item_id)
    if request.method == 'POST':
        item.product_id = request.form['product_id']
        item.original_purchase_invoice_item_id = request.form.get('original_purchase_invoice_item_id')
        item.quantity_returned = request.form['quantity_returned']
        item.price_per_unit_at_return = request.form['price_per_unit_at_return']
        item.gst_percentage_applied = request.form.get('gst_percentage_applied', 0.0)
        item.gst_amount_claimed_back_per_unit = request.form.get('gst_amount_claimed_back_per_unit', 0.0)
        item.item_sub_total_before_gst = request.form['item_sub_total_before_gst']
        item.item_total_gst_claimed_back = request.form['item_total_gst_claimed_back']
        item.item_final_value = request.form['item_final_value']
        db.session.commit()
        flash('Purchase return item updated!', 'success')
        return redirect(url_for('main.purchase_return_items', return_id=item.purchase_return_id))
    return render_template('purchase_returns/add_item.html', item=item, return_id=item.purchase_return_id)

@main.route('/purchase-return/items/delete/<int:item_id>', methods=['POST'])
def delete_purchase_return_item(item_id):
    item = PurchaseReturnItem.query.get_or_404(item_id)
    return_id = item.purchase_return_id
    db.session.delete(item)
    db.session.commit()
    flash('Purchase return item deleted!', 'success')
    return redirect(url_for('main.purchase_return_items', return_id=return_id))

# --- Sales Transactions Route ---
@main.route('/sales-transactions')
def sales_transactions():
    # Fetch sales invoices with customer details
    sales = db.session.query(
        SalesInvoice.id.label('sales_id'),
        SalesInvoice.invoice_number.label('transaction_id'),
        Customer.customer_name.label('customer_name'),
        Customer.id.label('customer_id'),
        SalesInvoice.total_invoice_amount.label('total_amount')
    ).join(Customer).all()

    # Fetch sales returns with customer details
    returns = db.session.query(
        SalesReturn.id.label('return_id'),
        SalesReturn.id.label('transaction_id'),
        Customer.customer_name.label('customer_name'),
        Customer.id.label('customer_id'),
        SalesReturn.final_amount_refunded.label('total_amount')
    ).join(Customer).all()

    # Convert to dictionaries for JSON serialization
    sales_data = [{
        'salesId': sale.sales_id,
        'transactionId': sale.transaction_id,
        'customerName': sale.customer_name,
        'customerId': sale.customer_id,
        'totalAmount': float(sale.total_amount)
    } for sale in sales] if sales else []

    returns_data = [{
        'returnId': ret.return_id,
        'transactionId': f'RTN{ret.transaction_id}',
        'customerName': ret.customer_name,
        'customerId': ret.customer_id,
        'totalAmount': float(ret.total_amount)
    } for ret in returns] if returns else []

    return render_template('sales_transactions.html', sales=sales_data, returns=returns_data)

# --- Purchase Transactions Route ---
@main.route('/purchase-transactions')
def purchase_transactions():
    # Fetch purchase invoices with supplier details
    purchases = db.session.query(
        PurchaseInvoice.id.label('purchase_id'),
        PurchaseInvoice.invoice_number.label('transaction_id'),
        Supplier.supplier_name.label('supplier_name'),
        Supplier.id.label('supplier_id'),
        PurchaseInvoice.total_invoice_amount.label('total_amount')
    ).join(Supplier).all()

    # Fetch purchase returns with supplier details
    purchase_returns = db.session.query(
        PurchaseReturn.id.label('return_id'),
        PurchaseReturn.id.label('transaction_id'),
        Supplier.supplier_name.label('supplier_name'),
        Supplier.id.label('supplier_id'),
        PurchaseReturn.final_amount_received.label('total_amount')
    ).join(Supplier).all()

    # Convert to dictionaries for JSON serialization
    purchase_data = [{
        'purchaseId': p.purchase_id,
        'transactionId': p.transaction_id,
        'supplierName': p.supplier_name,
        'supplierId': p.supplier_id,
        'totalAmount': float(p.total_amount)
    } for p in purchases] if purchases else []

    purchase_return_data = [{
        'returnId': r.return_id,
        'transactionId': f'RTN{r.transaction_id}',
        'supplierName': r.supplier_name,
        'supplierId': r.supplier_id,
        'totalAmount': float(r.total_amount)
    } for r in purchase_returns] if purchase_returns else []

    return render_template('purchase_transactions.html', purchaseData=purchase_data, purchaseReturnData=purchase_return_data)
