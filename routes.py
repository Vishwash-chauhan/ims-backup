# routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
from models import db, Product, Customer, User, SalesInvoice, SalesInvoiceItem, PurchaseInvoice, PurchaseInvoiceItem, PurchaseReturn, PurchaseReturnItem, Supplier, SalesReturn, SalesReturnItem
import re
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash
from utils.pdf_generator import generate_pdf_from_template

main = Blueprint('main', __name__)

# Admin-only decorator
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or str(current_user.role).lower() != 'admin':
            #flash('Admin access required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/')
@login_required
def index():
    return render_template('index.html') # Assumes index.html exists

# --- Product CRUD ---
@main.route('/products')
@login_required
def product_list():
    products = Product.query.filter_by(deleted=False).all()
    return render_template('view_products.html', products=products)

@main.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    error = None
    if request.method == 'POST':
        product_name = request.form['product_name'].strip()
        product_code = request.form['product_code'].strip()

        if not product_name:
            error = 'Product name is required.'
        elif not product_code:
            error = 'Product code is required.'
        else:
            # Check for duplicates
            existing_product_by_name = Product.query.filter_by(product_name=product_name, deleted=False).first()
            if existing_product_by_name:
                if not error: error = f"Product name '{product_name}' already exists."
            
            existing_product_by_code = Product.query.filter_by(product_code=product_code, deleted=False).first()
            if existing_product_by_code:
                if not error: error = (error + " " if error else "") + f"Product code '{product_code}' already exists."


        # Process reorder_level
        reorder_level_val = 0  # Default
        reorder_level_str = request.form.get('reorder_level')
        if reorder_level_str and reorder_level_str.strip():
            try:
                val = int(reorder_level_str)
                if val < 0:
                    if not error: error = 'Reorder Level cannot be negative.'
                else:
                    reorder_level_val = val
            except ValueError:
                if not error: error = 'Reorder Level must be a valid integer.'

        # Process current_stock
        current_stock_val = 0  # Default
        current_stock_str = request.form.get('current_stock')
        if current_stock_str and current_stock_str.strip():
            try:
                current_stock_val = int(current_stock_str)
                # Add validation like current_stock_val < 0 if needed
            except ValueError:
                if not error: error = 'Current Stock must be a valid integer.'

        # Process GST fields
        gst_available_val = request.form.get('gst_available', 'no')
        gst_percentage_val = 0.0  # Default for 'no' or if 'yes' but invalid

        if gst_available_val == 'yes':
            gst_percentage_str = request.form.get('gst_percentage')
            if not gst_percentage_str or not gst_percentage_str.strip():
                if not error: error = 'GST Percentage is required when GST is available.'
            else:
                try:
                    val = float(gst_percentage_str)
                    if not (0 <= val <= 100):
                        if not error: error = 'GST Percentage must be between 0 and 100.'
                    else:
                        gst_percentage_val = val
                except ValueError:
                    if not error: error = 'GST Percentage must be a valid number.'
        # If gst_available_val is 'no', gst_percentage_val remains 0.0

        if error:
            flash(error, 'danger')
            return render_template('new_product_form.html', error=error, request=request)

        product = Product(
            product_name=product_name,
            product_code=product_code,
            hsn_code=request.form.get('hsn_code'),
            measuring_units=request.form.get('measuring_units'),
            reorder_level=reorder_level_val,
            gst_available=gst_available_val,
            gst_percentage=gst_percentage_val,
            description=request.form.get('description'),
            current_stock=current_stock_val
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('main.add_product')) # Stay on the add product page
    return render_template('new_product_form.html', request=None)

@main.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    error = None
    if request.method == 'POST':
        product_name = request.form['product_name'].strip()
        product_code = request.form['product_code'].strip()
        if not product_name:
            error = 'Product name is required.'
        elif not product_code:
            error = 'Product code is required.'
        else:
            # Check for duplicates, excluding the current product
            existing_product_by_name = Product.query.filter(
                Product.id != product_id, 
                Product.product_name == product_name, 
                Product.deleted == False
            ).first()
            if existing_product_by_name:
                if not error: error = f"Another product with name '{product_name}' already exists."
            
            existing_product_by_code = Product.query.filter(Product.id != product_id, Product.product_code == product_code, Product.deleted == False).first()
            if existing_product_by_code:
                if not error: error = (error + " " if error else "") + f"Another product with code '{product_code}' already exists."

        # Process reorder_level
        reorder_level_val = product.reorder_level if product.reorder_level is not None else 0
        reorder_level_str = request.form.get('reorder_level')
        if 'reorder_level' in request.form: # Field was submitted
            if reorder_level_str and reorder_level_str.strip():
                try:
                    val = int(reorder_level_str)
                    if val < 0:
                        if not error: error = 'Reorder Level cannot be negative.'
                    else:
                        reorder_level_val = val
                except ValueError:
                    if not error: error = 'Reorder Level must be a valid integer.'
            else: # Submitted as empty string
                reorder_level_val = 0 

        # Process current_stock
        current_stock_val = product.current_stock if product.current_stock is not None else 0
        current_stock_str = request.form.get('current_stock')
        if 'current_stock' in request.form: # Field was submitted
            if current_stock_str and current_stock_str.strip():
                try:
                    current_stock_val = int(current_stock_str)
                except ValueError:
                    if not error: error = 'Current Stock must be a valid integer.'
            else: # Submitted as empty string
                current_stock_val = 0

        # Process GST fields
        gst_available_val = request.form.get('gst_available', 'no')
        gst_percentage_val = 0.0  # Default for 'no' or if 'yes' but invalid

        if gst_available_val == 'yes':
            gst_percentage_str = request.form.get('gst_percentage')
            if not gst_percentage_str or not gst_percentage_str.strip():
                if not error: error = 'GST Percentage is required when GST is available.'
            else:
                try:
                    val = float(gst_percentage_str)
                    if not (0 <= val <= 100):
                        if not error: error = 'GST Percentage must be between 0 and 100.'
                    else:
                        gst_percentage_val = val
                except ValueError:
                    if not error: error = 'GST Percentage must be a valid number.'
        # If gst_available_val is 'no', gst_percentage_val remains 0.0

        if error:
            flash(error, 'danger')
            return render_template('new_product_form.html', product=product, error=error, request=request)

        product.product_name = product_name
        product.product_code = product_code
        product.hsn_code = request.form.get('hsn_code')
        product.measuring_units = request.form.get('measuring_units')
        product.reorder_level = reorder_level_val
        product.gst_available = gst_available_val
        product.gst_percentage = gst_percentage_val
        product.description = request.form.get('description')
        product.current_stock = current_stock_val
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('main.product_list'))
    return render_template('new_product_form.html', product=product, request=None)

@main.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.deleted = True
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('main.product_list'))

# --- Customer CRUD ---
@main.route('/customers')
@login_required
def customer_list():
    customers = Customer.query.filter_by(deleted=False).all()
    return render_template('view_customers.html', customers=customers)

@main.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    error = None
    form_data = request.form if request.method == 'POST' else {}

    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '').strip()
        email_address = request.form.get('email_address', '').strip()
        contact_number = request.form.get('contact_number', '').strip()

        errors = []

        if not customer_name: # Keep name required, but allow duplicates
             errors.append('Customer name is required.')

        if contact_number:
            existing_customer_contact = Customer.query.filter_by(contact_number=contact_number, deleted=False).first()
            if existing_customer_contact:
                errors.append(f"Contact number '{contact_number}' already exists.")

        if email_address:
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email_address):
                errors.append("Invalid email address format.")
            else:
                # Check against all customers, including soft-deleted ones,
                # as the email_address field has a UNIQUE constraint in the database.
                existing_customer_email = Customer.query.filter_by(email_address=email_address).first()
                if existing_customer_email:
                    # For add_customer, any existing email is a duplicate.
                    errors.append(f"Email address '{email_address}' already exists.")

        # Add more server-side validation as needed for other fields
        if errors:
            error_message = '; '.join(errors)
            # flash(error_message, 'danger') # Removed: Error is passed directly to template
            return render_template('new_customer_form.html', error=error_message, form_data=form_data, customer=None)
        
        customer = Customer(
            customer_name=customer_name,
            contact_number=contact_number,
            email_address=email_address if email_address else None,
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
            description=request.form.get('description', '').strip()
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer added successfully!', 'success')
        return redirect(url_for('main.add_customer')) # Redirect back to the add customer page
    
    return render_template('new_customer_form.html', customer=None, form_data=form_data, error=error)

@main.route('/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    error = None
    form_data = request.form if request.method == 'POST' else {}

    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '').strip()
        email_address = request.form.get('email_address', '').strip()
        contact_number = request.form.get('contact_number', '').strip()

        errors = []

        if not customer_name:
            errors.append('Customer name is required.')
        else:
            existing_customer_name = Customer.query.filter(
                Customer.id != customer_id,
                Customer.customer_name == customer_name,
                Customer.deleted == False
            ).first()
            if existing_customer_name:
                errors.append(f"Another customer with name '{customer_name}' already exists.")

        if email_address:
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email_address):
                errors.append("Invalid email address format.")
            else:
                # Check against all other customers, including soft-deleted ones,
                # as the email_address field has a UNIQUE constraint.
                existing_customer_email = Customer.query.filter(
                    Customer.id != customer_id,
                    Customer.email_address == email_address
                ).first()
                if existing_customer_email:
                    errors.append(f"Another customer with email '{email_address}' already exists.")

        if errors:
            error_message = '; '.join(errors)
            # flash(error_message, 'danger') # Removed: Error is passed directly to template
            return render_template('new_customer_form.html', customer=customer, error=error_message, form_data=form_data)

        customer.customer_name = customer_name
        customer.contact_number = contact_number
        customer.email_address = email_address if email_address else None
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
        customer.description = request.form.get('description', '').strip()
        db.session.commit()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('main.customer_list'))
    return render_template('new_customer_form.html', customer=customer, form_data=form_data, error=error)

@main.route('/customers/delete/<int:customer_id>', methods=['POST'])
@login_required
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    # Prevent deletion if customer has related sales invoices
    if customer.sales_invoices:
        flash('Cannot delete customer: there are related sales invoices.', 'danger')
        return redirect(url_for('main.customer_list'))
    customer.deleted = True
    db.session.commit()
    flash('Customer deleted successfully!', 'success')
    return redirect(url_for('main.customer_list'))

# --- Supplier CRUD ---
@main.route('/suppliers')
@login_required
def supplier_list():
    suppliers = Supplier.query.filter_by(deleted=False).all()
    return render_template('view_suppliers.html', suppliers=suppliers)

@main.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    error = None
    form_data = request.form if request.method == 'POST' else {}

    if request.method == 'POST':
        supplier_name = form_data.get('supplier_name', '').strip()
        supplier_contact = form_data.get('supplier_contact', '').strip()
        email_address = form_data.get('email_address', '').strip()
        gst_available_val = form_data.get('gst_available', 'no')
        gst_number_val = form_data.get('gst_number', '').strip()

        errors = []

        if not supplier_name:
            errors.append('Supplier name is required.')
        # Removed check for existing supplier name to allow duplicates

        if supplier_contact:
            existing_contact = Supplier.query.filter_by(supplier_contact=supplier_contact, deleted=False).first()
            if existing_contact:
                errors.append(f"Supplier contact number '{supplier_contact}' already exists.")

        if email_address:
            # Basic email format validation (can be more robust if needed)
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email_address):
                errors.append("Invalid email address format.")
            else:
                existing_email = Supplier.query.filter_by(email_address=email_address, deleted=False).first()
                if existing_email:
                    errors.append(f"Email address '{email_address}' already exists for another supplier.")

        if gst_available_val == 'yes' and gst_number_val:
            existing_gst = Supplier.query.filter_by(gst_number=gst_number_val, deleted=False).first()
            if existing_gst:
                errors.append(f"GST number '{gst_number_val}' already exists for another supplier.")

        gst_available_val = form_data.get('gst_available', 'no')
        gst_number_val = form_data.get('gst_number', '').strip()
        if gst_available_val == 'yes':
            if not gst_number_val:
                errors.append('GST Number is required when GST is available.')
            elif not re.match(r"^[a-zA-Z0-9]{15}$", gst_number_val):
                errors.append('GST Number must be 15 alphanumeric characters.')

        pincode = form_data.get('address_pincode', '').strip()
        if pincode and not re.match(r"^\d{6}$", pincode):
            errors.append('Pincode must be 6 digits.')

        account_available_val = form_data.get('account_available', 'no')
        if account_available_val == 'yes':
            if not form_data.get('account_holder_name','').strip():
                errors.append("Account Holder's Name is required when account details are available.")
            if not form_data.get('account_number','').strip():
                errors.append("Account Number is required when account details are available.")
            ifsc_code = form_data.get('ifsc_code','').strip()
            if not ifsc_code:
                errors.append("IFSC Code is required when account details are available.")
            elif not re.match(r"^[A-Za-z]{4}0[A-Z0-9]{6}$", ifsc_code):
                 errors.append('Invalid IFSC Code format (e.g., ABCD0123456).')

        if errors:
            error_message = '; '.join(errors)
            return render_template('supplier_form.html', error=error_message, form_data=form_data)

        supplier = Supplier(
            supplier_name=supplier_name,
            supplier_contact=supplier_contact if supplier_contact else None,
            email_address=email_address if email_address else None,
            gst_available=gst_available_val,
            gst_number=gst_number_val if gst_available_val == 'yes' else None,
            address_line1=form_data.get('address_line1'),
            address_pincode=form_data.get('address_pincode'),
            address_city=form_data.get('address_city'),
            address_state=form_data.get('address_state'),
            address_country=form_data.get('address_country', 'India'),
            account_available=account_available_val,
            account_holder_name=form_data.get('account_holder_name'),
            account_number=form_data.get('account_number'),
            ifsc_code=form_data.get('ifsc_code'),
            branch=form_data.get('branch')
        )
        db.session.add(supplier)
        db.session.commit()
        flash('Supplier added successfully!', 'success')
        return redirect(url_for('main.add_supplier')) # Changed redirect to the same page

    return render_template('supplier_form.html', form_data=form_data, error=error)

@main.route('/suppliers/edit/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    error = None
    form_data = {}

    if request.method == 'POST':
        form_data = request.form
        supplier_name = form_data.get('supplier_name','').strip()
        supplier_contact = form_data.get('supplier_contact', '').strip()
        email_address = form_data.get('email_address', '').strip()
        gst_available_val = form_data.get('gst_available', 'no')
        gst_number_val = form_data.get('gst_number', '').strip()

        errors = []

        if not supplier_name:
            errors.append('Supplier name is required.')
        else:
            existing_supplier_by_name = Supplier.query.filter(
                Supplier.id != supplier_id,
                Supplier.supplier_name == supplier_name,
                Supplier.deleted == False
            ).first()
            if existing_supplier_by_name:
                errors.append(f"Another supplier with name '{supplier_name}' already exists.")

        if supplier_contact:
            existing_contact = Supplier.query.filter(
                Supplier.id != supplier_id,
                Supplier.supplier_contact == supplier_contact,
                Supplier.deleted == False
            ).first()
            if existing_contact:
                errors.append(f"Another supplier with contact number '{supplier_contact}' already exists.")

        if email_address:
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email_address):
                errors.append("Invalid email address format.")
            else:
                existing_email = Supplier.query.filter(
                    Supplier.id != supplier_id,
                    Supplier.email_address == email_address,
                    Supplier.deleted == False
                ).first()
                if existing_email:
                    errors.append(f"Another supplier with email '{email_address}' already exists.")

        if gst_available_val == 'yes' and gst_number_val:
            existing_gst = Supplier.query.filter(
                Supplier.id != supplier_id, Supplier.gst_number == gst_number_val, Supplier.deleted == False
            ).first()
            if existing_gst:
                errors.append(f"Another supplier with GST number '{gst_number_val}' already exists.")

            if not gst_number_val:
                errors.append('GST Number is required when GST is available.')
            elif not re.match(r"^[a-zA-Z0-9]{15}$", gst_number_val):
                errors.append('GST Number must be 15 alphanumeric characters.')

        pincode = form_data.get('address_pincode', '').strip()
        if pincode and not re.match(r"^\d{6}$", pincode):
            errors.append('Pincode must be 6 digits.')

        account_available_val = form_data.get('account_available', 'no')
        if account_available_val == 'yes':
            if not form_data.get('account_holder_name','').strip():
                errors.append("Account Holder's Name is required when account details are available.")
            if not form_data.get('account_number','').strip():
                errors.append("Account Number is required when account details are available.")
            ifsc_code = form_data.get('ifsc_code','').strip()
            if not ifsc_code:
                errors.append("IFSC Code is required when account details are available.")
            elif not re.match(r"^[A-Za-z]{4}0[A-Z0-9]{6}$", ifsc_code):
                 errors.append('Invalid IFSC Code format (e.g., ABCD0123456).')

        if errors:
            error_message = '; '.join(errors)
            return render_template('supplier_form.html', supplier=supplier, error=error_message, form_data=form_data)

        supplier.supplier_name = supplier_name
        supplier.supplier_contact = supplier_contact if supplier_contact else None
        supplier.email_address = email_address if email_address else None
        supplier.gst_available = gst_available_val
        supplier.gst_number = gst_number_val if gst_available_val == 'yes' else None
        supplier.address_line1 = form_data.get('address_line1')
        supplier.address_pincode = form_data.get('address_pincode')
        supplier.address_city = form_data.get('address_city')
        supplier.address_state = form_data.get('address_state')
        supplier.address_country = form_data.get('address_country', 'India')
        supplier.account_available = account_available_val
        supplier.account_holder_name = form_data.get('account_holder_name')
        supplier.account_number = form_data.get('account_number')
        supplier.ifsc_code = form_data.get('ifsc_code')
        supplier.branch = form_data.get('branch')
        db.session.commit()
        flash('Supplier updated successfully!', 'success')
        return redirect(url_for('main.supplier_list'))

    # For GET request, populate form_data from supplier object
    form_data = {
        'supplier_name': supplier.supplier_name,
        'supplier_contact': supplier.supplier_contact or '',
        'email_address': supplier.email_address or '',
        'gst_available': supplier.gst_available,
        'gst_number': supplier.gst_number or '',
        'address_line1': supplier.address_line1 or '',
        'address_pincode': supplier.address_pincode or '',
        'address_city': supplier.address_city or '',
        'address_state': supplier.address_state or '',
        'address_country': supplier.address_country or 'India',
        'account_available': supplier.account_available,
        'account_holder_name': supplier.account_holder_name or '',
        'account_number': supplier.account_number or '',
        'ifsc_code': supplier.ifsc_code or '',
        'branch': supplier.branch or ''
    }
    return render_template('supplier_form.html', supplier=supplier, form_data=form_data, error=error)

@main.route('/suppliers/delete/<int:supplier_id>', methods=['POST'])
@login_required
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    # Optional: Check for related entities before deleting
    if supplier.purchase_invoices or supplier.purchase_returns:
        flash('Cannot delete supplier: there are related purchase invoices or purchase returns.', 'danger')
        return redirect(url_for('main.supplier_list'))
    
    supplier.deleted = True # Soft delete
    db.session.commit()
    flash('Supplier deleted successfully!', 'success')
    return redirect(url_for('main.supplier_list'))


# --- SalesInvoice CRUD ---
@main.route('/sales-invoices')
@login_required
def sales_invoice_list():
    return redirect(url_for('main.sales_transactions'))

@main.route('/sales-invoices/add', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
def delete_sales_invoice(invoice_id):
    sales_invoice = SalesInvoice.query.get_or_404(invoice_id)
    db.session.delete(sales_invoice)
    db.session.commit()
    flash('Sales invoice deleted successfully!', 'success')
    return redirect(url_for('main.sales_invoice_list'))

# --- PurchaseInvoice CRUD ---
@main.route('/purchase-invoices')
@login_required
def purchase_invoice_list():
    return redirect(url_for('main.purchase_transactions'))

@main.route('/purchase-invoices/add', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
def delete_purchase_invoice(invoice_id):
    purchase_invoice = PurchaseInvoice.query.get_or_404(invoice_id)
    db.session.delete(purchase_invoice)
    db.session.commit()
    flash('Purchase invoice deleted successfully!', 'success')
    return redirect(url_for('main.purchase_invoice_list'))

# --- API Endpoints for Sales Entry Form ---

@main.route('/api/products', methods=['GET'])
@login_required
def api_products():
    """API endpoint to fetch all non-deleted products."""
    try:
        products = Product.query.filter_by(deleted=False).all()
        product_list = [            {
                "product_id": p.id,
                "product_name": p.product_name,
                "product_code": p.product_code,
                "price_per_unit": None,  # Price is typically set at sale time or fetched differently
                "gst_percentage": p.gst_percentage if p.gst_available == 'yes' else 0.0
            } for p in products
        ]
        return jsonify(product_list)
    except Exception as e:
        # Log the exception e
        return jsonify({"error": "Failed to fetch products"}), 500

@main.route('/api/product/<int:product_id>', methods=['GET'])
@login_required
def api_product_by_id(product_id):
    """API endpoint to fetch a product by ID."""
    try:
        product = Product.query.filter_by(id=product_id, deleted=False).first()
        if product:
            return jsonify({
                "product_id": product.id,
                "product_name": product.product_name,
                "product_code": product.product_code,
                "gst_percentage": product.gst_percentage if product.gst_available == 'yes' else 0.0
            })
        else:
            return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": "Failed to fetch product"}), 500

@main.route('/api/executives', methods=['GET'])
@login_required
def api_executives():
    """API endpoint to fetch all active users (assumed to be executives)."""
    try:
        # Adjust filtering if executives are identified by a specific role
        # e.g., User.query.filter_by(is_active=True, role='executive').all()
        executives = User.query.filter_by(is_active=True).all()
        executive_list = [
            {
                "executive_id": u.id,
                "full_name": u.full_name
            } for u in executives
        ]
        return jsonify(executive_list)
    except Exception as e:
        # Log the exception e
        return jsonify({"error": "Failed to fetch executives"}), 500

@main.route('/api/customer/by-contact/<string:contact_number>', methods=['GET'])
@login_required
def api_customer_by_contact(contact_number):
    """API endpoint to fetch a customer by contact number."""
    try:
        customer = Customer.query.filter_by(contact_number=contact_number, deleted=False).first()
        if customer:
            return jsonify({
                "customer_id": customer.id,
                "customer_name": customer.customer_name,
                "contact_number": customer.contact_number
            })
        else:
            return jsonify({"error": "Customer not found"}), 404
    except Exception as e:
        # Log the exception e
        return jsonify({"error": "Failed to fetch customer by contact"}), 500

@main.route('/api/supplier/by-contact/<string:contact_number>', methods=['GET'])
@login_required
def api_supplier_by_contact(contact_number):
    """API endpoint to fetch a supplier by contact number."""
    try:
        supplier = Supplier.query.filter_by(supplier_contact=contact_number, deleted=False).first()
        if supplier:
            return jsonify({
                "supplier_id": supplier.id,
                "supplier_name": supplier.supplier_name,
                "supplier_contact": supplier.supplier_contact
            })
        else:
            return jsonify({"error": "Supplier not found"}), 404
    except Exception as e:
        # Log the exception e
        return jsonify({"error": "Failed to fetch supplier by contact"}), 500

@main.route('/api/check_customer_exists', methods=['POST'])
@login_required
def api_check_customer_exists():
    """
    API endpoint to check if a customer field (e.g., name, email) already exists.
    Expects JSON: {"field": "customer_name" | "email_address", "value": "...", "customer_id": "..." | null}
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request. JSON data expected."}), 400

        field_to_check = data.get('field')
        value_to_check = data.get('value', '').strip()
        customer_id_str = data.get('customer_id') # This will be a string like 'null' or an actual ID

        if not field_to_check or not value_to_check:
            return jsonify({"error": "Missing 'field' or 'value' in request."}), 400

        # If checking customer_name for a NEW customer (customer_id is 'null' or not provided),
        # report that it doesn't exist for client-side validation purposes,
        # as server-side add_customer allows duplicate names.
        if field_to_check == 'customer_name' and (not customer_id_str or customer_id_str == 'null'):
            return jsonify({"exists": False})

        if field_to_check == 'customer_name':
            # For customer_name, uniqueness is typically checked against non-deleted, active records,
            # and in edit mode, it's against *other* non-deleted records.
            # The add_customer route allows duplicate names, and this API reflects that for new customers.
            query = Customer.query.filter_by(deleted=False).filter(Customer.customer_name == value_to_check)
        elif field_to_check == 'email_address':
            # For email_address, the database UNIQUE constraint applies to all records (deleted or not).
            # So, the check should not initially filter by deleted=False.
            query = Customer.query.filter(Customer.email_address == value_to_check)
        else:
            return jsonify({"error": "Invalid 'field' specified."}), 400

        # If editing (customer_id is provided and not 'null'), exclude the current customer.
        # This is relevant for customer_name in edit mode, and for other fields (like email) in both add/edit mode.
        if customer_id_str and customer_id_str != 'null':
            query = query.filter(Customer.id != int(customer_id_str))

        exists = query.first() is not None
        return jsonify({"exists": exists})
    except Exception as e:
        # Log the exception e (e.g., import logging; logging.error(f"Error in api_check_customer_exists: {e}"))
        return jsonify({"error": "Server error during check."}), 500

# --- End of API Endpoints ---

@main.route('/api/sales', methods=['POST'])
@login_required
def api_create_sales():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request. JSON data expected."}), 400

    # Basic validation
    required_fields = ['sales_date', 'executive_id', 'customer_id', 'mode_of_payment', 'payment_option', 'overall_discount_amount', 'amount_paid_by_customer', 'items']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
        if field == 'items' and (not isinstance(data[field], list) or not data[field]):
            return jsonify({"error": "No items provided for sale."}), 400
        elif field != 'items':
            # Allow 0 for overall_discount_amount and amount_paid_by_customer
            if field in ['overall_discount_amount', 'amount_paid_by_customer']:
                if data[field] is None or data[field] == '':
                    return jsonify({"error": f"Field '{field}' cannot be empty."}), 400
            else:
                if not data[field]:
                    return jsonify({"error": f"Field '{field}' cannot be empty."}), 400

    try:
        sales_date = datetime.strptime(data['sales_date'], '%Y-%m-%d').date()
        executive_id = int(data['executive_id'])
        customer_id = int(data['customer_id'])
        mode_of_payment = data['mode_of_payment']
        payment_option = data['payment_option']
        overall_discount_amount = float(data.get('overall_discount_amount', 0))
        amount_paid = float(data.get('amount_paid_by_customer', 0))
        notes = data.get('notes', '')
        if notes is None:
            notes = ''
        notes = str(notes).strip()
    except Exception as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400

    executive = User.query.get(executive_id)
    if not executive:
        return jsonify({"error": "Invalid executive ID."}), 400
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"error": "Invalid customer ID."}), 400

    # Generate a unique invoice number (simple example)
    invoice_number = f"SI-{int(datetime.utcnow().timestamp())}"

    # Calculate totals
    total_amount_before_gst = 0
    total_gst_amount = 0
    items_to_create = []
    for item in data['items']:
        try:
            product_id = int(item['product_id'])
            quantity_sold = float(item['quantity_sold'])
            price_per_unit_before_gst = float(item['price_per_unit_before_gst'])
        except Exception:
            return jsonify({"error": "Invalid item data (product_id, quantity, or price)."}), 400
        if quantity_sold <= 0 or price_per_unit_before_gst < 0:
            return jsonify({"error": "Quantity must be positive and price non-negative for all items."}), 400
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": f"Product ID {product_id} not found."}), 400
        
        # Ensure gst_percentage is properly handled
        gst_percentage = 0.0
        if product.gst_available == 'yes' and product.gst_percentage is not None:
            gst_percentage = float(product.gst_percentage)
            
        item_sub_total_before_gst = quantity_sold * price_per_unit_before_gst
        item_total_gst_amount = item_sub_total_before_gst * (gst_percentage / 100)
        item_final_amount = item_sub_total_before_gst + item_total_gst_amount
        total_amount_before_gst += item_sub_total_before_gst
        total_gst_amount += item_total_gst_amount
        items_to_create.append({
            'product_id': product_id,
            'quantity_sold': quantity_sold,
            'price_per_unit_before_gst': item['price_per_unit_before_gst'],
            'gst_percentage': gst_percentage,
            'gst_amount_per_unit': price_per_unit_before_gst * (gst_percentage / 100),
            'item_discount_amount': 0.0,  # No per-item discount in this form
            'item_sub_total_before_gst': item_sub_total_before_gst,
            'item_total_gst_amount': item_total_gst_amount,
            'item_final_amount': item_final_amount
        })

    net_amount_before_gst = total_amount_before_gst - overall_discount_amount
    if net_amount_before_gst < 0:
        return jsonify({"error": "Discount cannot exceed total amount before GST."}), 400
    total_invoice_amount = net_amount_before_gst + total_gst_amount

    # Payment validation
    if payment_option == 'full-payment':
        if abs(amount_paid - total_invoice_amount) > 0.01:
            return jsonify({"error": "For full payment, amount paid must match total payable amount."}), 400
    elif payment_option == 'partial-payment':
        if amount_paid <= 0:
            return jsonify({"error": "For partial payment, amount paid must be greater than zero."}), 400
        if amount_paid > total_invoice_amount:
            return jsonify({"error": "Partial amount paid cannot be greater than total payable amount."}), 400
    else:
        return jsonify({"error": "Invalid payment option."}), 400

    try:
        db.session.begin_nested()
        new_invoice = SalesInvoice(
            invoice_number=invoice_number,
            invoice_date=sales_date,
            customer_id=customer_id,
            executive_id=executive_id,
            total_amount_before_gst=total_amount_before_gst,
            total_gst_amount=total_gst_amount,
            overall_discount_amount=overall_discount_amount,
            total_invoice_amount=total_invoice_amount,
            payment_status='Paid' if payment_option == 'full-payment' else 'Partial',
            notes=notes
        )
        db.session.add(new_invoice)
        db.session.flush()  # To get new_invoice.id
        for item in items_to_create:
            db.session.add(SalesInvoiceItem(
                sales_invoice_id=new_invoice.id,
                product_id=item['product_id'],
                quantity_sold=item['quantity_sold'],
                price_per_unit_before_gst=item['price_per_unit_before_gst'],
                gst_percentage=item['gst_percentage'],
                gst_amount_per_unit=item['gst_amount_per_unit'],
                item_discount_amount=item['item_discount_amount'],
                item_sub_total_before_gst=item['item_sub_total_before_gst'],
                item_total_gst_amount=item['item_total_gst_amount'],
                item_final_amount=item['item_final_amount']
            ))
            # Update product stock
            product = Product.query.get(item['product_id'])
            if product:
                current_stock = product.current_stock if product.current_stock is not None else 0
                product.current_stock = current_stock - item['quantity_sold']
        db.session.commit()
        # Generate PDF and store in DB
        # Fetch the invoice with related data
        invoice = SalesInvoice.query.options(
            db.joinedload(SalesInvoice.customer),
            db.joinedload(SalesInvoice.items)
        ).filter_by(id=new_invoice.id).first()

        # Prepare items for the bill
        items = []
        for item in invoice.items:
            items.append({
                'product_name': item.product.product_name,
                'quantity': item.quantity_sold,
                'unit_price': float(item.price_per_unit_before_gst),
                'subtotal': float(item.item_sub_total_before_gst)
            })

        bill = {
            'id': invoice.invoice_number,
            'date': invoice.invoice_date.strftime('%Y-%m-%d'),
            'customer_name': invoice.customer.customer_name,
            'customer_address': invoice.customer.billing_address_line1,
            'customer_contact': invoice.customer.contact_number,
            'items': items,
            'subtotal': float(invoice.total_amount_before_gst),
            'tax_rate': float(items[0]['unit_price'] if items else 0),  # Adjust if you want GST %
            'tax_amount': float(invoice.total_gst_amount),
            'discount': float(invoice.overall_discount_amount or 0),
            'total_amount': float(invoice.total_invoice_amount),
            'payment_method': invoice.payment_status,
            'logo_path': 'img/company_logo.png'
        }
        context = {
            'bill': bill,
            'title': 'Sales Bill',
            'bill_type_label': 'Bill To'
        }

        # Generate PDF and store in DB
        pdf_bytes = generate_pdf_from_template('bills/sales_bill_template.html', context)
        invoice.bill_pdf = pdf_bytes
        db.session.commit()
        return jsonify({"message": "Sales invoice created successfully!", "invoice_number": invoice_number}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred while creating the sales invoice: {str(e)}"}), 500

@main.route('/api/purchases', methods=['POST'])
@login_required
def api_create_purchases():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request. JSON data expected."}), 400

    # Basic validation
    required_fields = [
        'purchase_date', 'supplier_id', 'mode_of_payment', 'payment_option',
        'overall_discount_amount', 'amount_paid', 'items'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
        if field == 'items' and (not isinstance(data[field], list) or not data[field]):
            return jsonify({"error": "No items provided for purchase."}), 400
        elif field != 'items':
            if field in ['overall_discount_amount', 'amount_paid']:
                if data[field] is None or data[field] == '':
                    return jsonify({"error": f"Field '{field}' cannot be empty."}), 400
            else:
                if not data[field]:
                    return jsonify({"error": f"Field '{field}' cannot be empty."}), 400

    try:
        purchase_date = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date()
        supplier_id = int(data['supplier_id'])
        mode_of_payment = data['mode_of_payment']
        payment_option = data['payment_option']
        overall_discount_amount = float(data.get('overall_discount_amount', 0))
        amount_paid = float(data.get('amount_paid', 0))
        notes = data.get('notes', '').strip()
    except Exception as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400

    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        return jsonify({"error": "Invalid supplier ID."}), 400

    # Generate a unique invoice number (simple example)
    invoice_number = f"PI-{int(datetime.utcnow().timestamp())}"

    # Calculate totals
    total_amount_before_gst = 0
    total_gst_amount = 0
    items_to_create = []
    for item in data['items']:
        try:
            product_id = int(item['product_id'])
            quantity_purchased = float(item['quantity_purchased'])
            price_per_unit_before_gst = float(item['price_per_unit_before_gst'])
        except Exception:
            return jsonify({"error": "Invalid item data (product_id, quantity, or price)."}), 400
        if quantity_purchased <= 0 or price_per_unit_before_gst < 0:
            return jsonify({"error": "Quantity must be positive and price non-negative for all items."}), 400
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": f"Product ID {product_id} not found."}), 400
        gst_percentage = float(product.gst_percentage) if product.gst_available == 'yes' else 0.0
        item_sub_total_before_gst = quantity_purchased * price_per_unit_before_gst
        item_total_gst_amount = item_sub_total_before_gst * (gst_percentage / 100)
        item_final_amount = item_sub_total_before_gst + item_total_gst_amount
        total_amount_before_gst += item_sub_total_before_gst
        total_gst_amount += item_total_gst_amount
        items_to_create.append({
            'product_id': product_id,
            'quantity_purchased': quantity_purchased,
            'price_per_unit_before_gst': item['price_per_unit_before_gst'],
            'gst_percentage': gst_percentage,
            'gst_amount_per_unit': price_per_unit_before_gst * (gst_percentage / 100),
            'item_discount_amount': 0.0,  # No per-item discount in this form
            'item_sub_total_before_gst': item_sub_total_before_gst,
            'item_total_gst_amount': item_total_gst_amount,
            'item_final_amount': item_final_amount
        })

    net_amount_before_gst = total_amount_before_gst - overall_discount_amount
    if net_amount_before_gst < 0:
        return jsonify({"error": "Discount cannot exceed total amount before GST."}), 400
    total_invoice_amount = net_amount_before_gst + total_gst_amount

    # Payment validation
    if payment_option == 'full-payment':
        if abs(amount_paid - total_invoice_amount) > 0.01:
            return jsonify({"error": "For full payment, amount paid must match total payable amount."}), 400
    elif payment_option == 'partial-payment':
        if amount_paid <= 0:
            return jsonify({"error": "For partial payment, amount paid must be greater than zero."}), 400
        if amount_paid > total_invoice_amount:
            return jsonify({"error": "Partial amount paid cannot be greater than total payable amount."}), 400
    else:
        return jsonify({"error": "Invalid payment option."}), 400

    try:
        db.session.begin_nested()
        new_invoice = PurchaseInvoice(
            invoice_number=invoice_number,
            invoice_date=purchase_date,
            supplier_id=supplier_id,
            total_amount_before_gst=total_amount_before_gst,
            total_gst_amount=total_gst_amount,
            overall_discount_amount=overall_discount_amount,
            total_invoice_amount=total_invoice_amount,
            payment_status='Paid' if payment_option == 'full-payment' else 'Partial',
            notes=notes
        )
        db.session.add(new_invoice)
        db.session.flush()  # To get new_invoice.id
        for item in items_to_create:
            db.session.add(PurchaseInvoiceItem(
                purchase_invoice_id=new_invoice.id,
                product_id=item['product_id'],
                quantity_purchased=item['quantity_purchased'],
                price_per_unit_before_gst=item['price_per_unit_before_gst'],
                gst_percentage=item['gst_percentage'],
                gst_amount_per_unit=item['gst_amount_per_unit'],
                item_discount_amount=item['item_discount_amount'],
                item_sub_total_before_gst=item['item_sub_total_before_gst'],
                item_total_gst_amount=item['item_total_gst_amount'],
                item_final_amount=item['item_final_amount']
            ))            # Update product stock
            product = Product.query.get(item['product_id'])
            if product:
                product.current_stock = (product.current_stock or 0) + item['quantity_purchased']
        db.session.commit()
        return jsonify({"message": "Purchase invoice created successfully!", "purchase_id": new_invoice.id, "invoice_number": new_invoice.invoice_number}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred while creating the purchase invoice: {str(e)}"}), 500

# --- Dashboard and Transaction Views ---
@main.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Dashboard view with links to main sections"""
    return render_template('dashboard.html')

@main.route('/sales-entry', methods=['GET', 'POST'])
@login_required
def sales_entry():
    """Sales entry form for creating new sales"""
    if request.method == 'POST':
        # Handle sales entry form submission
        # This could redirect to add_sales_invoice or handle the logic here
        return redirect(url_for('main.add_sales_invoice'))
    return render_template('sales_entry.html')

@main.route('/purchases-form', methods=['GET', 'POST'])
@login_required
def purchases_form():
    """Purchase form for creating new purchases"""
    if request.method == 'POST':
        # Handle purchase form submission
        # This could redirect to add_purchase_invoice or handle the logic here
        return redirect(url_for('main.add_purchase_invoice'))
    return render_template('purchase_form.html')

@main.route('/purchase-return', methods=['GET', 'POST'])
@login_required
def purchase_return():
    """Purchase return form for processing returns"""
    if request.method == 'POST':
        # Handle purchase return form submission
        # Add purchase return logic here
        try:
            purchase_return = PurchaseReturn(
                return_date=request.form['return_date'],
                original_invoice_id=request.form.get('original_invoice_id'),
                supplier_id=request.form['supplier_id'],
                total_return_amount=request.form.get('total_return_amount', 0.0),
                notes=request.form.get('notes')
            )
            db.session.add(purchase_return)
            db.session.commit()
            flash('Purchase return processed successfully!', 'success')
            return redirect(url_for('main.purchase_transactions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing purchase return: {str(e)}', 'error')
    return render_template('purchase_return_form.html')

@main.route('/sales-return', methods=['GET', 'POST'])
@login_required
def sales_return():
    """Sales return form for processing returns"""
    if request.method == 'POST':
        # Handle sales return form submission
        try:
            sales_return = SalesReturn(
                return_date=request.form['return_date'],
                original_invoice_id=request.form.get('original_invoice_id'),
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
            db.session.flush()  # Flush to get the sales_return.id
            
            # Process individual product items
            products_data = request.form.to_dict()
            for key in products_data:
                if key.startswith('products[') and key.endswith('][product_id]'):
                    # Extract the product index
                    import re
                    match = re.search(r'products\[(\d+)\]', key)
                    if match:
                        index = match.group(1)
                        product_id = products_data.get(f'products[{index}][product_id]')
                        quantity_returned = products_data.get(f'products[{index}][quantity_returned]')
                        price_per_unit = products_data.get(f'products[{index}][price_per_unit]')
                        gst_percentage = products_data.get(f'products[{index}][gst_percentage]')
                        amount = products_data.get(f'products[{index}][amount]')
                        
                        if product_id and quantity_returned:
                            # Calculate the item totals
                            price_per_unit = float(price_per_unit) if price_per_unit else 0.0
                            quantity = int(quantity_returned)
                            gst_percent = float(gst_percentage) if gst_percentage else 0.0
                            
                            item_sub_total = price_per_unit * quantity
                            gst_amount_per_unit = (price_per_unit * gst_percent) / 100
                            item_total_gst = gst_amount_per_unit * quantity
                            item_final_amount = item_sub_total + item_total_gst
                            
                            sales_return_item = SalesReturnItem(
                                sales_return_id=sales_return.id,
                                product_id=int(product_id),
                                quantity_returned=quantity,
                                price_per_unit_at_return=price_per_unit,
                                gst_percentage_applied=gst_percent,
                                gst_amount_refunded_per_unit=gst_amount_per_unit,
                                item_sub_total_before_gst=item_sub_total,
                                item_total_gst_amount=item_total_gst,
                                item_final_amount=item_final_amount
                            )
                            db.session.add(sales_return_item)
            
            db.session.commit()
            flash('Sales return processed successfully!', 'success')
            return redirect(url_for('main.sales_transactions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing sales return: {str(e)}', 'error')
    return render_template('sales_return_form.html')

@main.route('/sales-transactions')
@login_required
def sales_transactions():
    """View all sales transactions"""
    sales_invoices = SalesInvoice.query.order_by(SalesInvoice.invoice_date.desc(), SalesInvoice.created_at.desc()).all()
    sales_returns = SalesReturn.query.order_by(SalesReturn.return_date.desc(), SalesReturn.created_at.desc()).all()
    return render_template(
        'view_sales.html',
        sales_invoices=sales_invoices,
        sales_returns=sales_returns
    )

@main.route('/purchase-transactions')
@login_required
def purchase_transactions():
    """View all purchase transactions"""
    purchase_invoices = PurchaseInvoice.query.order_by(PurchaseInvoice.invoice_date.desc(), PurchaseInvoice.created_at.desc()).all()
    purchase_returns = PurchaseReturn.query.order_by(PurchaseReturn.return_date.desc(), PurchaseReturn.created_at.desc()).all()
    return render_template(
        'view_purchase.html',
        purchase_invoices=purchase_invoices,
        purchase_returns=purchase_returns
    )

@main.route('/api/invoice-details/<string:invoice_number>', methods=['GET'])
@login_required
def get_invoice_details(invoice_number):
    """Get invoice details by invoice number for returns (supports both sales and purchase invoices)"""
    try:
        # Try to find the sales invoice first
        sales_invoice = SalesInvoice.query.filter_by(invoice_number=invoice_number).first()
        if sales_invoice:
            invoice_items = SalesInvoiceItem.query.filter_by(sales_invoice_id=sales_invoice.id).all()
            invoice_data = {
                "invoice_id": sales_invoice.id,
                "invoice_number": sales_invoice.invoice_number,
                "invoice_date": sales_invoice.invoice_date.strftime("%Y-%m-%d"),
                "customer_id": sales_invoice.customer_id,
                "customer_name": sales_invoice.customer.customer_name if sales_invoice.customer else "",
                "executive_id": sales_invoice.executive_id,
                "executive_name": sales_invoice.executive.full_name if sales_invoice.executive else "",
                "total_amount": float(sales_invoice.total_invoice_amount),
                "type": "sales",
                "items": []
            }
            for item in invoice_items:
                invoice_data["items"].append({
                    "product_id": item.product_id,
                    "product_name": item.product.product_name if item.product else "",
                    "quantity_sold": item.quantity_sold,
                    "price_per_unit": float(item.price_per_unit_before_gst),
                    "gst_percentage": float(item.gst_percentage),
                    "sub_total": float(item.item_sub_total_before_gst),
                    "gst_amount": float(item.item_total_gst_amount),
                    "total_amount": float(item.item_final_amount)
                })
            return jsonify(invoice_data), 200
        # If not found, try purchase invoice
        purchase_invoice = PurchaseInvoice.query.filter_by(invoice_number=invoice_number).first()
        if purchase_invoice:
            invoice_items = PurchaseInvoiceItem.query.filter_by(purchase_invoice_id=purchase_invoice.id).all()
            invoice_data = {
                "invoice_id": purchase_invoice.id,
                "invoice_number": purchase_invoice.invoice_number,
                "invoice_date": purchase_invoice.invoice_date.strftime("%Y-%m-%d"),
                "supplier_id": purchase_invoice.supplier_id,
                "supplier_name": purchase_invoice.supplier.supplier_name if purchase_invoice.supplier else "",
                "supplier_contact": purchase_invoice.supplier.supplier_contact if purchase_invoice.supplier else "",
                "executive_id": None,  # Not tracked for purchase invoices
                "executive_name": None,
                "total_amount": float(purchase_invoice.total_invoice_amount),
                "type": "purchase",
                "items": []
            }
            for item in invoice_items:
                invoice_data["items"].append({
                    "product_id": item.product_id,
                    "product_name": item.product.product_name if item.product else "",
                    "quantity_sold": item.quantity_purchased,  # For compatibility with return forms
                    "price_per_unit": float(item.price_per_unit_before_gst),
                    "gst_percentage": float(item.gst_percentage),
                    "sub_total": float(item.item_sub_total_before_gst),
                    "gst_amount": float(item.item_total_gst_amount),
                    "total_amount": float(item.item_final_amount)
                })
            return jsonify(invoice_data), 200
        return jsonify({"error": "Invoice not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Error fetching invoice details: {str(e)}"}), 500

@main.route('/api/sales-return', methods=['POST'])
@login_required
def api_create_sales_return():
    """Handle JSON-based sales return form submission"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request. JSON data expected."}), 400

        # Basic validation
        required_fields = ['return_date', 'customer_id', 'products']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        if not isinstance(data['products'], list) or not data['products']:
            return jsonify({"error": "No products provided for return."}), 400

        # Create the sales return record
        sales_return = SalesReturn(
            return_date=datetime.strptime(data['return_date'], '%Y-%m-%d').date(),
            original_invoice_id=data.get('original_invoice_id'),
            customer_id=data['customer_id'],
            executive_id=data.get('executive_id'),
            return_reason=data.get('return_reason'),
            total_items_value_before_gst=float(data.get('total_items_value_before_gst', 0.0)),
            total_gst_reversed=float(data.get('total_gst_reversed', 0.0)),
            net_refundable_amount=float(data.get('net_refundable_amount', 0.0)),
            mode_of_refund=data.get('mode_of_refund'),
            refund_option=data.get('refund_option', 'full-refund'),
            partial_refund_amount_input=float(data.get('partial_refund_amount_input', 0.0)) if data.get('partial_refund_amount_input') else None,
            final_amount_refunded=float(data.get('final_amount_refunded', 0.0)),
            notes=data.get('notes')
        )
        
        db.session.add(sales_return)
        db.session.flush()  # Flush to get the sales_return.id

        # Process individual product items
        for product_data in data['products']:
            if product_data.get('product_id') and product_data.get('quantity_returned'):
                product_id = int(product_data['product_id'])
                quantity = int(product_data['quantity_returned'])
                price_per_unit = float(product_data.get('price_per_unit', 0.0))
                gst_percent = float(product_data.get('gst_percentage', 0.0))
                
                # Calculate the item totals
                item_sub_total = price_per_unit * quantity
                gst_amount_per_unit = (price_per_unit * gst_percent) / 100
                item_total_gst = gst_amount_per_unit * quantity
                item_final_amount = item_sub_total + item_total_gst
                
                sales_return_item = SalesReturnItem(
                    sales_return_id=sales_return.id,
                    product_id=product_id,
                    quantity_returned=quantity,
                    price_per_unit_at_return=price_per_unit,
                    gst_percentage_applied=gst_percent,
                    gst_amount_refunded_per_unit=gst_amount_per_unit,
                    item_sub_total_before_gst=item_sub_total,
                    item_total_gst_amount=item_total_gst,
                    item_final_amount=item_final_amount
                )
                db.session.add(sales_return_item)
                
                # Update product stock (add back returned quantity)
                product = Product.query.get(product_id)
                if product:
                    product.stock_quantity += quantity

        db.session.commit()
        
        return jsonify({
            "message": "Sales return processed successfully!",
            "return_id": sales_return.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error processing sales return: {str(e)}"}), 500

# --- Authentication and User Management ---

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = 'remember' in request.form
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_active:
                error = 'Account is inactive.'
            else:
                login_user(user, remember=remember)
                flash('Logged in successfully!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('main.index'))
        else:
            error = 'Invalid email or password.'
    return render_template('auth/login.html', error=error)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
@login_required
@admin_required
def register():
    error = None
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        phone = request.form.get('phone')  # <-- get phone from form

        # Hash the password
        password_hash = generate_password_hash(password)

        # Create new user instance (make sure User model has a phone field)
        new_user = User(
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            phone=phone,  # <-- include phone here
            role=role,
            is_active=True
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            error = str(e)
            return render_template('auth/register.html', error=error)
    return render_template('auth/register.html', error=error)

@main.route('/users')
@login_required
@admin_required
def user_list():
    users = User.query.all()
    return render_template('admin/user_list.html', users=users)

@main.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

