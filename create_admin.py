from flask import Flask
from models import db, User
from config import Config

def create_admin():
    """Create an admin user if it doesn't exist"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        # Check if admin exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if admin:
            print('Admin user already exists')
            return

        # Create admin user
        admin = User(
            email='admin@example.com',
            full_name='Administrator',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')  # You should change this in production
        
        db.session.add(admin)
        db.session.commit()
        print('Admin user created successfully')

if __name__ == '__main__':
    create_admin()