from flask import Flask
from config import Config
from models import db
from auth import auth, init_auth

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)  # Initialize db with app

# Initialize authentication
init_auth(app)

# Import routes after app is defined, so routes can use this app instance
from routes import main

# Register blueprints
app.register_blueprint(main)
app.register_blueprint(auth)

if __name__ == '__main__':
    app.run(debug=True)
