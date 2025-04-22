from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
CORS(app)

# SQLite veritabanı yapılandırması
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assistant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Veritabanı modelleri
class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)

# API rotaları
@app.route('/api/reminders', methods=['GET'])
def get_reminders():
    reminders = Reminder.query.all()
    return jsonify([{
        'id': r.id,
        'title': r.title,
        'description': r.description,
        'due_date': r.due_date.isoformat(),
        'is_completed': r.is_completed
    } for r in reminders])

@app.route('/api/reminders', methods=['POST'])
def create_reminder():
    data = request.get_json()
    reminder = Reminder(
        title=data['title'],
        description=data.get('description', ''),
        due_date=datetime.fromisoformat(data['due_date']),
        is_completed=False
    )
    db.session.add(reminder)
    db.session.commit()
    return jsonify({
        'id': reminder.id,
        'title': reminder.title,
        'description': reminder.description,
        'due_date': reminder.due_date.isoformat(),
        'is_completed': reminder.is_completed
    }), 201

# Veritabanını oluştur
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 