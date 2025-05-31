from flask import Flask
from config import Config
from models import db
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)  # Initialize db with app
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'warning'

# Import routes after app is defined, so routes can use this app instance
from routes import main

# Register blueprints
app.register_blueprint(main)

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from documents.documents import documents_bp
app.register_blueprint(documents_bp)

if __name__ == "__main__":
    app.run(debug=True)
