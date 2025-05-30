"""Add phone, is_admin, is_active to users table

Revision ID: 55cf0345cfe7
Revises: 
Create Date: 2025-05-30 15:05:08.160162

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '55cf0345cfe7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
        batch_op.alter_column('deleted',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False,
               existing_server_default=sa.text("'0'"))

    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
        batch_op.alter_column('deleted',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False,
               existing_server_default=sa.text("'0'"))
        batch_op.drop_index(batch_op.f('idx_product_code'))
        batch_op.drop_index(batch_op.f('idx_product_name'))

    with op.batch_alter_table('purchase_invoice_items', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.drop_constraint(batch_op.f('purchase_invoice_items_ibfk_1'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'purchase_invoices', ['purchase_invoice_id'], ['id'])

    with op.batch_alter_table('purchase_invoices', schema=None) as batch_op:
        batch_op.alter_column('invoice_date',
               existing_type=sa.DATE(),
               nullable=True)
        batch_op.alter_column('created_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    with op.batch_alter_table('purchase_return_items', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.drop_constraint(batch_op.f('purchase_return_items_ibfk_3'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('purchase_return_items_ibfk_1'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'purchase_invoice_items', ['original_purchase_invoice_item_id'], ['id'])
        batch_op.create_foreign_key(None, 'purchase_returns', ['purchase_return_id'], ['id'])

    with op.batch_alter_table('purchase_returns', schema=None) as batch_op:
        batch_op.alter_column('total_items_value_before_gst',
               existing_type=mysql.DECIMAL(precision=12, scale=2),
               nullable=True,
               existing_server_default=sa.text("'0.00'"))
        batch_op.alter_column('total_gst_claimed_back',
               existing_type=mysql.DECIMAL(precision=10, scale=2),
               nullable=True,
               existing_server_default=sa.text("'0.00'"))
        batch_op.alter_column('net_amount_receivable',
               existing_type=mysql.DECIMAL(precision=12, scale=2),
               nullable=True,
               existing_server_default=sa.text("'0.00'"))
        batch_op.alter_column('created_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    with op.batch_alter_table('sales_invoice_items', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.drop_constraint(batch_op.f('sales_invoice_items_ibfk_1'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'sales_invoices', ['sales_invoice_id'], ['id'])

    with op.batch_alter_table('sales_invoices', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
        batch_op.drop_index(batch_op.f('invoice_number'))
        batch_op.create_index(batch_op.f('ix_sales_invoices_invoice_number'), ['invoice_number'], unique=True)
        batch_op.drop_constraint(batch_op.f('sales_invoices_ibfk_2'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['executive_id'], ['id'])

    with op.batch_alter_table('sales_return_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('gst_amount_refunded_per_unit', sa.Numeric(precision=10, scale=2), nullable=True))
        batch_op.add_column(sa.Column('item_total_gst_amount', sa.Numeric(precision=10, scale=2), nullable=False))
        batch_op.add_column(sa.Column('item_final_amount', sa.Numeric(precision=10, scale=2), nullable=False))
        batch_op.alter_column('created_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.drop_constraint(batch_op.f('sales_return_items_ibfk_3'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('sales_return_items_ibfk_1'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'sales_invoice_items', ['original_sales_invoice_item_id'], ['id'])
        batch_op.create_foreign_key(None, 'sales_returns', ['sales_return_id'], ['id'])
        batch_op.drop_column('gst_amount_reversed_per_unit')
        batch_op.drop_column('item_total_gst_reversed')
        batch_op.drop_column('item_final_value')

    with op.batch_alter_table('sales_returns', schema=None) as batch_op:
        batch_op.alter_column('total_items_value_before_gst',
               existing_type=mysql.DECIMAL(precision=12, scale=2),
               nullable=True,
               existing_server_default=sa.text("'0.00'"))
        batch_op.alter_column('total_gst_reversed',
               existing_type=mysql.DECIMAL(precision=10, scale=2),
               nullable=True,
               existing_server_default=sa.text("'0.00'"))
        batch_op.alter_column('net_refundable_amount',
               existing_type=mysql.DECIMAL(precision=12, scale=2),
               nullable=True,
               existing_server_default=sa.text("'0.00'"))
        batch_op.alter_column('created_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
        batch_op.drop_constraint(batch_op.f('sales_returns_ibfk_3'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['executive_id'], ['id'])

    with op.batch_alter_table('supplier_products', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('supplier_products_ibfk_2'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('supplier_products_ibfk_1'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'products', ['product_id'], ['id'])
        batch_op.create_foreign_key(None, 'suppliers', ['supplier_id'], ['id'])

    with op.batch_alter_table('suppliers', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
        batch_op.alter_column('deleted',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False,
               existing_server_default=sa.text("'0'"))
        batch_op.drop_index(batch_op.f('idx_supplier_name'))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone', sa.String(length=20), nullable=False))
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=True))
        batch_op.alter_column('password_hash',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)
        batch_op.alter_column('created_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=mysql.TIMESTAMP(),
               type_=sa.DateTime(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
        batch_op.drop_index(batch_op.f('email'))
        batch_op.create_unique_constraint(None, ['phone'])
        batch_op.drop_column('role')
        batch_op.drop_column('email')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', mysql.VARCHAR(length=255), nullable=True))
        batch_op.add_column(sa.Column('role', mysql.VARCHAR(length=50), nullable=True))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.create_index(batch_op.f('email'), ['email'], unique=True)
        batch_op.alter_column('updated_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('password_hash',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)
        batch_op.drop_column('is_admin')
        batch_op.drop_column('phone')

    with op.batch_alter_table('suppliers', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('idx_supplier_name'), ['supplier_name'], unique=False)
        batch_op.alter_column('deleted',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True,
               existing_server_default=sa.text("'0'"))
        batch_op.alter_column('updated_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('supplier_products', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('supplier_products_ibfk_1'), 'suppliers', ['supplier_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
        batch_op.create_foreign_key(batch_op.f('supplier_products_ibfk_2'), 'products', ['product_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')

    with op.batch_alter_table('sales_returns', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('sales_returns_ibfk_3'), 'users', ['executive_id'], ['id'], ondelete='SET NULL')
        batch_op.alter_column('updated_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('net_refundable_amount',
               existing_type=mysql.DECIMAL(precision=12, scale=2),
               nullable=False,
               existing_server_default=sa.text("'0.00'"))
        batch_op.alter_column('total_gst_reversed',
               existing_type=mysql.DECIMAL(precision=10, scale=2),
               nullable=False,
               existing_server_default=sa.text("'0.00'"))
        batch_op.alter_column('total_items_value_before_gst',
               existing_type=mysql.DECIMAL(precision=12, scale=2),
               nullable=False,
               existing_server_default=sa.text("'0.00'"))

    with op.batch_alter_table('sales_return_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('item_final_value', mysql.DECIMAL(precision=10, scale=2), nullable=False))
        batch_op.add_column(sa.Column('item_total_gst_reversed', mysql.DECIMAL(precision=10, scale=2), nullable=False))
        batch_op.add_column(sa.Column('gst_amount_reversed_per_unit', mysql.DECIMAL(precision=10, scale=2), server_default=sa.text("'0.00'"), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('sales_return_items_ibfk_1'), 'sales_returns', ['sales_return_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(batch_op.f('sales_return_items_ibfk_3'), 'sales_invoice_items', ['original_sales_invoice_item_id'], ['id'], ondelete='SET NULL')
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.drop_column('item_final_amount')
        batch_op.drop_column('item_total_gst_amount')
        batch_op.drop_column('gst_amount_refunded_per_unit')

    with op.batch_alter_table('sales_invoices', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('sales_invoices_ibfk_2'), 'users', ['executive_id'], ['id'], ondelete='SET NULL')
        batch_op.drop_index(batch_op.f('ix_sales_invoices_invoice_number'))
        batch_op.create_index(batch_op.f('invoice_number'), ['invoice_number'], unique=True)
        batch_op.alter_column('updated_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('sales_invoice_items', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('sales_invoice_items_ibfk_1'), 'sales_invoices', ['sales_invoice_id'], ['id'], ondelete='CASCADE')
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('purchase_returns', schema=None) as batch_op:
        batch_op.alter_column('updated_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('net_amount_receivable',
               existing_type=mysql.DECIMAL(precision=12, scale=2),
               nullable=False,
               existing_server_default=sa.text("'0.00'"))
        batch_op.alter_column('total_gst_claimed_back',
               existing_type=mysql.DECIMAL(precision=10, scale=2),
               nullable=False,
               existing_server_default=sa.text("'0.00'"))
        batch_op.alter_column('total_items_value_before_gst',
               existing_type=mysql.DECIMAL(precision=12, scale=2),
               nullable=False,
               existing_server_default=sa.text("'0.00'"))

    with op.batch_alter_table('purchase_return_items', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('purchase_return_items_ibfk_1'), 'purchase_returns', ['purchase_return_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(batch_op.f('purchase_return_items_ibfk_3'), 'purchase_invoice_items', ['original_purchase_invoice_item_id'], ['id'], ondelete='SET NULL')
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('purchase_invoices', schema=None) as batch_op:
        batch_op.alter_column('updated_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('invoice_date',
               existing_type=sa.DATE(),
               nullable=False)

    with op.batch_alter_table('purchase_invoice_items', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('purchase_invoice_items_ibfk_1'), 'purchase_invoices', ['purchase_invoice_id'], ['id'], ondelete='CASCADE')
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('idx_product_name'), ['product_name'], unique=False)
        batch_op.create_index(batch_op.f('idx_product_code'), ['product_code'], unique=False)
        batch_op.alter_column('deleted',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True,
               existing_server_default=sa.text("'0'"))
        batch_op.alter_column('updated_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.alter_column('deleted',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True,
               existing_server_default=sa.text("'0'"))
        batch_op.alter_column('updated_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=mysql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    # ### end Alembic commands ###
