from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database configuration (using SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///personal_assistant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Basic route
@app.route('/')
def home():
    return jsonify({
        "status": "success",
        "message": "Personal Assistant API is running"
    })

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True) 