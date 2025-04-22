from flask import Flask
from flask_cors import CORS
from models.models import db
from routes.api import api  # Import yolunu düzelttik

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database configuration (using SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///personal_assistant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# API blueprint'ini kaydet
app.register_blueprint(api, url_prefix='/api')

# Veritabanı tablolarını oluştur
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 