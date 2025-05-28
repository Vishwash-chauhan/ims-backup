from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(255), nullable=False)
    contact_number = db.Column(db.String(20))
    email_address = db.Column(db.String(255), unique=True)
    billing_address_line1 = db.Column(db.String(255))
    billing_pincode = db.Column(db.String(10))
    billing_city = db.Column(db.String(100))
    billing_state = db.Column(db.String(100))
    billing_country = db.Column(db.String(100), default='India')
    shipping_address_line1 = db.Column(db.String(255))
    shipping_pincode = db.Column(db.String(10))
    shipping_city = db.Column(db.String(100))
    shipping_state = db.Column(db.String(100))
    shipping_country = db.Column(db.String(100), default='India')
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    sales_invoices = db.relationship('SalesInvoice', backref='customer', lazy=True, cascade='all, delete')
    sales_returns = db.relationship('SalesReturn', backref='customer', lazy=True, cascade='all, delete')

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    product_code = db.Column(db.String(50), unique=True)
    hsn_code = db.Column(db.String(20))
    product_image_path = db.Column(db.String(255))
    measuring_units = db.Column(db.String(50))
    reorder_level = db.Column(db.Integer)
    gst_available = db.Column(db.Enum('yes', 'no'), default='no')
    gst_percentage = db.Column(db.Numeric(5,2), default=0.00)
    description = db.Column(db.Text)
    current_stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    purchase_invoice_items = db.relationship('PurchaseInvoiceItem', backref='product', lazy=True, cascade='all, delete')
    sales_invoice_items = db.relationship('SalesInvoiceItem', backref='product', lazy=True, cascade='all, delete')
    purchase_return_items = db.relationship('PurchaseReturnItem', backref='product', lazy=True, cascade='all, delete')
    sales_return_items = db.relationship('SalesReturnItem', backref='product', lazy=True, cascade='all, delete')
    suppliers = db.relationship('Supplier', secondary='supplier_products', back_populates='products')

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(255), nullable=False)
    supplier_contact = db.Column(db.String(50))
    gst_available = db.Column(db.Enum('yes', 'no'), default='no')
    gst_number = db.Column(db.String(15))
    address_line1 = db.Column(db.String(255))
    address_pincode = db.Column(db.String(10))
    address_city = db.Column(db.String(100))
    address_state = db.Column(db.String(100))
    address_country = db.Column(db.String(100), default='India')
    account_available = db.Column(db.Enum('yes', 'no'), default='no')
    account_holder_name = db.Column(db.String(255))
    account_number = db.Column(db.String(50))
    ifsc_code = db.Column(db.String(20))
    branch = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    purchase_invoices = db.relationship('PurchaseInvoice', backref='supplier', lazy=True, cascade='all, delete')
    purchase_returns = db.relationship('PurchaseReturn', backref='supplier', lazy=True, cascade='all, delete')
    products = db.relationship('Product', secondary='supplier_products', back_populates='suppliers')

class SupplierProduct(db.Model):
    __tablename__ = 'supplier_products'
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)

class PurchaseInvoice(db.Model):
    __tablename__ = 'purchase_invoices'
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_date = db.Column(db.Date)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    total_amount_before_gst = db.Column(db.Numeric(12,2), default=0.00)
    total_gst_amount = db.Column(db.Numeric(10,2), default=0.00)
    overall_discount_amount = db.Column(db.Numeric(10,2), default=0.00)
    total_invoice_amount = db.Column(db.Numeric(12,2), nullable=False)
    payment_status = db.Column(db.String(50), default='Pending')
    bill_copy_path = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items = db.relationship('PurchaseInvoiceItem', backref='purchase_invoice', lazy=True)
    purchase_returns = db.relationship('PurchaseReturn', backref='original_purchase_invoice', lazy=True, foreign_keys='PurchaseReturn.original_purchase_invoice_id')

class PurchaseInvoiceItem(db.Model):
    __tablename__ = 'purchase_invoice_items'
    id = db.Column(db.Integer, primary_key=True)
    purchase_invoice_id = db.Column(db.Integer, db.ForeignKey('purchase_invoices.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_purchased = db.Column(db.Integer, nullable=False)
    price_per_unit_before_gst = db.Column(db.Numeric(10,2), nullable=False)
    gst_percentage = db.Column(db.Numeric(5,2), default=0.00)
    gst_amount_per_unit = db.Column(db.Numeric(10,2), default=0.00)
    item_discount_amount = db.Column(db.Numeric(10,2), default=0.00)
    item_sub_total_before_gst = db.Column(db.Numeric(10,2), nullable=False)
    item_total_gst_amount = db.Column(db.Numeric(10,2), nullable=False)
    item_final_amount = db.Column(db.Numeric(10,2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PurchaseReturn(db.Model):
    __tablename__ = 'purchase_returns'
    id = db.Column(db.Integer, primary_key=True)
    return_date = db.Column(db.Date, nullable=False)
    original_purchase_invoice_id = db.Column(db.Integer, db.ForeignKey('purchase_invoices.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    return_reason = db.Column(db.Text)
    total_items_value_before_gst = db.Column(db.Numeric(12,2), default=0.00)
    total_gst_claimed_back = db.Column(db.Numeric(10,2), default=0.00)
    net_amount_receivable = db.Column(db.Numeric(12,2), default=0.00)
    mode_of_refund_received = db.Column(db.String(50))
    refund_receipt_option = db.Column(db.Enum('full-amount','partial-amount'), default='full-amount')
    partial_amount_received_input = db.Column(db.Numeric(12,2))
    final_amount_received = db.Column(db.Numeric(12,2), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items = db.relationship('PurchaseReturnItem', backref='purchase_return', lazy=True)

class PurchaseReturnItem(db.Model):
    __tablename__ = 'purchase_return_items'
    id = db.Column(db.Integer, primary_key=True)
    purchase_return_id = db.Column(db.Integer, db.ForeignKey('purchase_returns.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    original_purchase_invoice_item_id = db.Column(db.Integer, db.ForeignKey('purchase_invoice_items.id'))
    quantity_returned = db.Column(db.Integer, nullable=False)
    price_per_unit_at_return = db.Column(db.Numeric(10,2), nullable=False)
    gst_percentage_applied = db.Column(db.Numeric(5,2), default=0.00)
    gst_amount_claimed_back_per_unit = db.Column(db.Numeric(10,2), default=0.00)
    item_sub_total_before_gst = db.Column(db.Numeric(10,2), nullable=False)
    item_total_gst_claimed_back = db.Column(db.Numeric(10,2), nullable=False)
    item_final_value = db.Column(db.Numeric(10,2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SalesInvoice(db.Model):
    __tablename__ = 'sales_invoices'
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    invoice_date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    executive_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total_amount_before_gst = db.Column(db.Numeric(12,2), default=0.00)
    total_gst_amount = db.Column(db.Numeric(10,2), default=0.00)
    overall_discount_amount = db.Column(db.Numeric(10,2), default=0.00)
    total_invoice_amount = db.Column(db.Numeric(12,2), nullable=False)
    payment_status = db.Column(db.String(50), default='Pending')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items = db.relationship('SalesInvoiceItem', backref='sales_invoice', lazy=True)
    sales_returns = db.relationship('SalesReturn', backref='original_invoice', lazy=True, foreign_keys='SalesReturn.original_invoice_id')

class SalesInvoiceItem(db.Model):
    __tablename__ = 'sales_invoice_items'
    id = db.Column(db.Integer, primary_key=True)
    sales_invoice_id = db.Column(db.Integer, db.ForeignKey('sales_invoices.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    price_per_unit_before_gst = db.Column(db.Numeric(10,2), nullable=False)
    gst_percentage = db.Column(db.Numeric(5,2), default=0.00)
    gst_amount_per_unit = db.Column(db.Numeric(10,2), default=0.00)
    item_discount_amount = db.Column(db.Numeric(10,2), default=0.00)
    item_sub_total_before_gst = db.Column(db.Numeric(10,2), nullable=False)
    item_total_gst_amount = db.Column(db.Numeric(10,2), nullable=False)
    item_final_amount = db.Column(db.Numeric(10,2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SalesReturn(db.Model):
    __tablename__ = 'sales_returns'
    id = db.Column(db.Integer, primary_key=True)
    return_date = db.Column(db.Date, nullable=False)
    original_invoice_id = db.Column(db.Integer, db.ForeignKey('sales_invoices.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    executive_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    return_reason = db.Column(db.Text)
    total_items_value_before_gst = db.Column(db.Numeric(12,2), default=0.00)
    total_gst_reversed = db.Column(db.Numeric(10,2), default=0.00)
    net_refundable_amount = db.Column(db.Numeric(12,2), default=0.00)
    mode_of_refund = db.Column(db.String(50))
    refund_option = db.Column(db.Enum('full-refund','partial-refund'), default='full-refund')
    partial_refund_amount_input = db.Column(db.Numeric(12,2))
    final_amount_refunded = db.Column(db.Numeric(12,2), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items = db.relationship('SalesReturnItem', backref='sales_return', lazy=True)

class SalesReturnItem(db.Model):
    __tablename__ = 'sales_return_items'
    id = db.Column(db.Integer, primary_key=True)
    sales_return_id = db.Column(db.Integer, db.ForeignKey('sales_returns.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    original_sales_invoice_item_id = db.Column(db.Integer, db.ForeignKey('sales_invoice_items.id'))
    quantity_returned = db.Column(db.Integer, nullable=False)
    price_per_unit_at_return = db.Column(db.Numeric(10,2), nullable=False)
    gst_percentage_applied = db.Column(db.Numeric(5,2), default=0.00)
    gst_amount_reversed_per_unit = db.Column(db.Numeric(10,2), default=0.00)
    item_sub_total_before_gst = db.Column(db.Numeric(10,2), nullable=False)
    item_total_gst_reversed = db.Column(db.Numeric(10,2), nullable=False)
    item_final_value = db.Column(db.Numeric(10,2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True)
    role = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    password_hash = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sales_invoices = db.relationship('SalesInvoice', backref='executive', lazy=True, foreign_keys='SalesInvoice.executive_id')
    sales_returns = db.relationship('SalesReturn', backref='executive', lazy=True, foreign_keys='SalesReturn.executive_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

# ...add more models as needed for your app
