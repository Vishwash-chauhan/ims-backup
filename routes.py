# routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import uuid
import re # Added for email validation
from models import db, Product, Customer, User, SalesInvoice, SalesInvoiceItem, PurchaseInvoice, PurchaseInvoiceItem, SalesReturn, SalesReturnItem, PurchaseReturn, PurchaseReturnItem, Supplier # Add Supplier here

main = Blueprint('main', __name__)

@main.route('/')
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

        if not customer_name:
            errors.append('Customer name is required.')
        else:
            existing_customer_name = Customer.query.filter_by(customer_name=customer_name, deleted=False).first()
            if existing_customer_name:
                errors.append(f"Customer name '{customer_name}' already exists.")

        if contact_number:
            existing_customer_contact = Customer.query.filter_by(contact_number=contact_number, deleted=False).first()
            if existing_customer_contact:
                errors.append(f"Contact number '{contact_number}' already exists.")

        if email_address:
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email_address):
                errors.append("Invalid email address format.")
            else:
                existing_customer_email = Customer.query.filter_by(email_address=email_address, deleted=False).first()
                if existing_customer_email:
                    # Check if the email belongs to the same customer being edited (not applicable for add)
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
                existing_customer_email = Customer.query.filter(
                    Customer.id != customer_id,
                    Customer.email_address == email_address,
                    Customer.deleted == False
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
    # Prevent deletion if customer has related sales invoices or sales returns
    if customer.sales_invoices or customer.sales_returns:
        flash('Cannot delete customer: there are related sales invoices or sales returns.', 'danger')
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

        errors = []

        if not supplier_name:
            errors.append('Supplier name is required.')
        # Removed check for existing supplier name to allow duplicates

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
            supplier_contact=form_data.get('supplier_contact'),
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
            return render_template('supplier_form.html', supplier=supplier, error=error_message, form_data=form_data)

        supplier.supplier_name = supplier_name
        supplier.supplier_contact = form_data.get('supplier_contact')
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

    flash('Supplier deleted successfully!', 'success')
    return redirect(url_for('main.supplier_list'))

# --- API Endpoints for Sales Entry ---
@main.route('/api/products')
@login_required
def api_products():
    products = Product.query.filter_by(deleted=False).all()
    return jsonify([{
        'product_id': p.id,
        'product_name': p.product_name,
        'product_code': p.product_code,
        'price_per_unit': None,  # Frontend expects this, can be null if not stored directly
        'gst_percentage': float(p.gst_percentage) if p.gst_percentage is not None else 0.0
    } for p in products])

@main.route('/api/executives')
@login_required
def api_executives():
    # Assuming executives are users. Adjust if there's a specific 'executive' role.
    # You might want to filter by role, e.g., User.query.filter_by(role='executive', is_active=True).all()
    executives = User.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': u.id,
        'full_name': u.full_name
    } for u in executives])

@main.route('/api/customer/<int:customer_id>')
@login_required
def api_customer_details(customer_id):
    customer = Customer.query.filter_by(id=customer_id, deleted=False).first()
    if customer:
        return jsonify({'customer_id': customer.id, 'customer_name': customer.customer_name})
    return jsonify({'error': 'Customer not found'}), 404

@main.route('/api/customer/by-contact/<string:contact_number>')
@login_required
def api_customer_details_by_contact(contact_number):
    # Basic validation for contact_number can be added here (e.g., length, digits only)
    customer = Customer.query.filter_by(contact_number=contact_number, deleted=False).first()
    if customer:
        return jsonify({
            'customer_id': customer.id,
            'customer_name': customer.customer_name,
            'contact_number': customer.contact_number # Optionally return contact too
        })
    return jsonify({'error': 'Customer not found with this contact number'}), 404


# --- API Endpoints ---
@main.route('/api/check-customer-exists', methods=['POST'])
@login_required
def api_check_customer_exists():
    data = request.get_json()
    field = data.get('field')
    value = data.get('value')
    customer_id = data.get('customer_id') # Will be None for 'add' mode, or an ID for 'edit'

    if not field or not value:
        return jsonify({'exists': False, 'error': 'Missing field or value'}), 400

    query = Customer.query.filter_by(deleted=False)

    if field == 'customer_name':
        query = query.filter(Customer.customer_name == value)
    elif field == 'email_address':
        query = query.filter(Customer.email_address == value)
    else:
        return jsonify({'exists': False, 'error': 'Invalid field specified'}), 400

    if customer_id:
        try:
            query = query.filter(Customer.id != int(customer_id))
        except ValueError:
            return jsonify({'exists': False, 'error': 'Invalid customer_id format'}), 400
            
    return jsonify({'exists': query.first() is not None})

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

# --- SalesReturn CRUD ---
@main.route('/sales-returns')
@login_required
def sales_return_list():
    sales_returns = SalesReturn.query.all()
    return render_template('sales_returns/list.html', sales_returns=sales_returns)

@main.route('/sales-returns/add', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
def delete_sales_return(return_id):
    sales_return = SalesReturn.query.get_or_404(return_id)
    db.session.delete(sales_return)
    db.session.commit()
    flash('Sales return deleted successfully!', 'success')
    return redirect(url_for('main.sales_return_list'))

# --- PurchaseReturn CRUD ---
@main.route('/purchase-returns')
@login_required
def purchase_return_list():
    purchase_returns = PurchaseReturn.query.all()
    return render_template('purchase_returns/list.html', purchase_returns=purchase_returns)

@main.route('/purchase-returns/add', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
def delete_purchase_return(return_id):
    purchase_return = PurchaseReturn.query.get_or_404(return_id)
    db.session.delete(purchase_return)
    db.session.commit()
    flash('Purchase return deleted successfully!', 'success')
    return redirect(url_for('main.purchase_return_list'))

# --- User CRUD ---
@main.route('/users')
@login_required
def user_list():
    users = User.query.all()
    return render_template('users/list.html', users=users)

@main.route('/users/add', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('main.user_list'))

# --- Transactions and sensitive pages ---
@main.route('/sales-entry')
@login_required
def sales_entry():
    return render_template('sales_entry.html')

@main.route('/purchase-form')
@login_required
def purchases_form():
    return render_template('purchase_form.html')

@main.route('/sales-return')
@login_required
def sales_return():
    return render_template('sales_return.html')

@main.route('/purchase-return')
@login_required
def purchase_return():
    return render_template('purchase_return_form.html')

@main.route('/dashboard')
@login_required
def dashboard():
    # Explicitly check if the current user is an admin
    # Assumes your User model (current_user) has a 'role' attribute or similar
    if not hasattr(current_user, 'role') or current_user.role != 'admin':
        flash("You do not have permission to access this page. Only admins can view the dashboard.", "danger")
        # Redirect to a general page like index to avoid potential loops with the login page
        return redirect(url_for('main.index'))
    return render_template('admin/dashboard.html')

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
    ).join(Customer).order_by(SalesInvoice.created_at.desc()).all()

    # Fetch sales returns with customer details
    returns = db.session.query(
        SalesReturn.id.label('return_id'),
        SalesReturn.id.label('transaction_id'), # This will be the SalesReturn.id
        Customer.customer_name.label('customer_name'),
        Customer.id.label('customer_id'),
        SalesReturn.final_amount_refunded.label('total_amount')
    ).join(Customer).order_by(SalesReturn.created_at.desc()).all()

    # Convert to dictionaries for JSON serialization
    sales_data = [{
        'salesId': sale.sales_id,
        'transactionId': sale.transaction_id, # This is SalesInvoice.invoice_number
        'customerName': sale.customer_name,
        'customerId': sale.customer_id,
        'totalAmount': float(sale.total_amount)
    } for sale in sales] if sales else []

    returns_data = [{
        'returnId': ret.return_id,
        'transactionId': f'RTN-{ret.return_id}', # Use SalesReturn.id for a unique return transaction ID
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
    ).join(Supplier).order_by(PurchaseInvoice.created_at.desc()).all() # Added sorting

    # Fetch purchase returns with supplier details
    purchase_returns_data = db.session.query(
        PurchaseReturn.id.label('return_id'),
        PurchaseReturn.id.label('transaction_id'), # This will be PurchaseReturn.id
        Supplier.supplier_name.label('supplier_name'),
        Supplier.id.label('supplier_id'),
        PurchaseReturn.final_amount_received.label('total_amount')
    ).join(Supplier).order_by(PurchaseReturn.created_at.desc()).all() # Added sorting

    # Convert to dictionaries for JSON serialization
    purchase_data = [{
        'purchaseId': p.purchase_id,
        'transactionId': p.transaction_id, # This is PurchaseInvoice.invoice_number
        'supplierName': p.supplier_name,
        'supplierId': p.supplier_id,
        'totalAmount': float(p.total_amount)
    } for p in purchases] if purchases else []

    purchase_return_data_list = [{ # Renamed to avoid conflict
        'returnId': r.return_id,
        'transactionId': f'PRTN-{r.return_id}', # Use PurchaseReturn.id for a unique return transaction ID
        'supplierName': r.supplier_name,
        'supplierId': r.supplier_id,
        'totalAmount': float(r.total_amount)
    } for r in purchase_returns_data] if purchase_returns_data else []

    return render_template('purchase_transactions.html', purchaseData=purchase_data, purchaseReturnData=purchase_return_data_list)

@main.route('/base')
def base_preview():
    return render_template('base.html')
