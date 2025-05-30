from flask import Flask
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)  # Initialize db with app

# Import routes after app is defined, so routes can use this app instance
from routes import main

# Register blueprints
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)
