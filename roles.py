from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    """Decorator to check if user has one of the required roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Role definitions
ROLE_ADMIN = 'admin'
ROLE_MANAGER = 'manager'
ROLE_SALES = 'sales'
ROLE_INVENTORY = 'inventory'

# Role permissions
ROLE_PERMISSIONS = {
    ROLE_ADMIN: [
        'manage_users',
        'manage_roles',
        'view_reports',
        'manage_products',
        'manage_customers',
        'manage_suppliers',
        'manage_sales',
        'manage_purchases',
        'manage_returns'
    ],
    ROLE_MANAGER: [
        'view_reports',
        'manage_products',
        'manage_customers',
        'manage_suppliers',
        'manage_sales',
        'manage_purchases',
        'manage_returns'
    ],
    ROLE_SALES: [
        'view_products',
        'manage_customers',
        'manage_sales',
        'manage_sales_returns'
    ],
    ROLE_INVENTORY: [
        'manage_products',
        'manage_suppliers',
        'manage_purchases',
        'manage_purchase_returns'
    ]
}

def has_permission(permission):
    """Check if current user has the required permission"""
    if not current_user.is_authenticated:
        return False
    if current_user.role == ROLE_ADMIN:
        return True
    return permission in ROLE_PERMISSIONS.get(current_user.role, [])
