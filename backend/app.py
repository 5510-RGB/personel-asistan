from flask import Flask
from flask_cors import CORS
from models.models import db
from routes.api import api

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# SQLite veritabanı yapılandırması
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///personal_assistant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Veritabanını başlat
db.init_app(app)

# API Blueprint'i kaydet
app.register_blueprint(api, url_prefix='/api')

# Veritabanı tablolarını oluştur
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 