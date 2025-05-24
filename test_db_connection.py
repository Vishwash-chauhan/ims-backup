from app import app, db

with app.app_context():
    db.session.execute('SELECT 1')
    print('Database connection successful!')
