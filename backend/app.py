from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)

# CORS ayarları
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     allow_credentials=True,
     supports_credentials=True)

# SQLite veritabanı yapılandırması
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'gizli-anahtar-123')  # Gerçek uygulamada environment variable kullanın

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Kullanıcı modeli
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # Hash'lenmiş şifre için daha uzun alan
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(20), nullable=False)  # 'user' veya 'assistant'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'sender': self.sender,
            'timestamp': self.timestamp.isoformat()
        }

# Not modeli
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }

def validate_password(password):
    if len(password) < 8:
        return False, "Şifre en az 8 karakter uzunluğunda olmalıdır"
    if not re.search(r"[A-Z]", password):
        return False, "Şifre en az bir büyük harf içermelidir"
    if not re.search(r"[a-z]", password):
        return False, "Şifre en az bir küçük harf içermelidir"
    if not re.search(r"\d", password):
        return False, "Şifre en az bir rakam içermelidir"
    return True, ""

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

# Veritabanını oluştur
with app.app_context():
    db.create_all()

# Kayıt olma endpoint'i
@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    print("Register endpoint'ine istek geldi")  # Debug log
    
    if request.method == 'OPTIONS':
        print("OPTIONS isteği alındı")  # Debug log
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response

    try:
        print("Request headers:", request.headers)  # Debug log
        data = request.get_json()
        print("Gelen veri:", data)  # Debug log

        if not data:
            print("Veri alınamadı")  # Debug log
            return jsonify({"error": "Veri alınamadı"}), 400

        email = data.get("email")
        username = data.get("username")
        password = data.get("password")

        print(f"Email: {email}, Username: {username}")  # Debug log

        # Email ve kullanıcı adı kontrolü
        if User.query.filter_by(email=email).first():
            print("Email zaten kayıtlı")  # Debug log
            return jsonify({"error": "Bu email adresi zaten kayıtlı"}), 400
        
        if User.query.filter_by(username=username).first():
            print("Kullanıcı adı zaten kullanılıyor")  # Debug log
            return jsonify({"error": "Bu kullanıcı adı zaten kullanılıyor"}), 400

        # Şifre validasyonu
        is_valid, message = validate_password(password)
        if not is_valid:
            print(f"Şifre hatası: {message}")  # Debug log
            return jsonify({"error": message}), 400

        # Email validasyonu
        if not validate_email(email):
            print("Geçersiz email formatı")  # Debug log
            return jsonify({"error": "Geçersiz email formatı"}), 400

        # Yeni kullanıcı oluştur
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        # Veritabanına kaydet
        try:
            db.session.add(new_user)
            db.session.commit()
            print("Kullanıcı başarıyla kaydedildi")  # Debug log
            response = jsonify({"message": "Kayıt başarılı"})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 201
        except Exception as e:
            print(f"Veritabanı hatası: {str(e)}")  # Debug log
            db.session.rollback()
            return jsonify({"error": f"Kayıt sırasında bir hata oluştu: {str(e)}"}), 500
    except Exception as e:
        print(f"Genel hata: {str(e)}")  # Debug log
        return jsonify({"error": f"Beklenmeyen bir hata oluştu: {str(e)}"}), 500

# Giriş yapma endpoint'i
@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response
        
    try:
        data = request.get_json()
        print("Login isteği:", data)  # Debug log
        
        user = User.query.filter_by(username=data['username']).first()
        
        if user and check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity=user.id)
            response = jsonify({
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
        
        return jsonify({'error': 'Geçersiz kullanıcı adı veya şifre'}), 401
    except Exception as e:
        print("Login hatası:", str(e))  # Debug log
        return jsonify({'error': str(e)}), 500

# Kullanıcı bilgilerini getirme endpoint'i
@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    }), 200

@app.route('/')
def home():
    return jsonify({
        "message": "Yapay Zeka Destekli Kişisel Asistan API'sine Hoş Geldiniz",
        "status": "active"
    })

@app.route('/api/status')
def status():
    return jsonify({
        "service": "Personal Assistant API",
        "status": "running"
    })

@app.route('/api/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.timestamp).all()
    return jsonify([message.to_dict() for message in messages])

@app.route('/api/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
        
    message = Message(
        content=data['content'],
        sender=data.get('sender', 'user')
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify(message.to_dict()), 201

# Hava durumu endpoint'i
@app.route('/api/weather', methods=['GET'])
@jwt_required()
def get_weather():
    # Örnek hava durumu verisi
    weather_data = {
        'temperature': 23,
        'description': 'Güneşli',
        'icon': '☀️'
    }
    return jsonify(weather_data)

# Hatırlatıcılar endpoint'i
@app.route('/api/reminders', methods=['GET'])
@jwt_required()
def get_reminders():
    # Örnek hatırlatıcı verileri
    reminders = [
        {
            'title': 'Toplantı',
            'time': '14:00'
        },
        {
            'title': 'Alışveriş',
            'time': '18:30'
        }
    ]
    return jsonify(reminders)

# E-postalar endpoint'i
@app.route('/api/emails', methods=['GET'])
@jwt_required()
def get_emails():
    # Örnek e-posta verileri
    emails = [
        {
            'subject': 'Proje Güncellemesi',
            'sender': 'patron@firma.com'
        },
        {
            'subject': 'Haftalık Rapor',
            'sender': 'rapor@firma.com'
        }
    ]
    return jsonify(emails)

# Haberler endpoint'i
@app.route('/api/news', methods=['GET'])
@jwt_required()
def get_news():
    # Örnek haber verileri
    news = [
        {
            'title': 'Yeni Teknoloji Gelişmeleri',
            'source': 'Tech News'
        },
        {
            'title': 'Ekonomi Haberleri',
            'source': 'Ekonomi Gazetesi'
        }
    ]
    return jsonify(news)

# Not ekleme endpoint'i
@app.route('/api/notes', methods=['POST'])
@jwt_required()
def add_note():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    if not data or 'content' not in data:
        return jsonify({'error': 'Not içeriği gerekli'}), 400
        
    note = Note(
        content=data['content'],
        user_id=user_id
    )
    
    db.session.add(note)
    db.session.commit()
    
    return jsonify(note.to_dict()), 201

# Hatırlatıcı ekleme endpoint'i
@app.route('/api/reminders', methods=['POST'])
@jwt_required()
def add_reminder():
    data = request.get_json()
    
    if not data or 'title' not in data or 'time' not in data:
        return jsonify({'error': 'Başlık ve zaman gerekli'}), 400
        
    reminder = {
        'title': data['title'],
        'time': data['time']
    }
    
    return jsonify(reminder), 201

@app.route('/api/chat', methods=['POST'])
@jwt_required()
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')

        # Basit yanıt mantığı
        if 'merhaba' in user_message.lower():
            response = "Merhaba! Size nasıl yardımcı olabilirim?"
        elif 'hava' in user_message.lower():
            response = "Hava durumu bilgisini kontrol ediyorum..."
        elif 'saat' in user_message.lower():
            response = f"Şu anki saat: {datetime.now().strftime('%H:%M:%S')}"
        elif 'tarih' in user_message.lower():
            response = f"Bugünün tarihi: {datetime.now().strftime('%d/%m/%Y')}"
        elif 'yardım' in user_message.lower():
            response = """Size şu konularda yardımcı olabilirim:
1. Hava durumu bilgisi
2. Saat ve tarih bilgisi
3. Hatırlatıcı oluşturma
4. Not alma
5. Haberleri görüntüleme
6. E-posta kontrolü"""
        else:
            response = "Üzgünüm, bu konuda size yardımcı olamıyorum. Başka bir soru sorabilir misiniz?"

        return jsonify({
            'response': response,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 