from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash
import re
import random
import requests
import imaplib
import email
from email.header import decode_header
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets

app = Flask(__name__)

# CORS ayarları
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     allow_credentials=True,
     supports_credentials=True)

# SQLite veritabanı yapılandırması
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'gizli-anahtar-123'  # Gerçek uygulamada güvenli bir anahtar kullanın
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# NewsAPI için gerekli ayarlar
NEWS_API_KEY = '851eb8871030409cbea1e4501848b2a6'

# E-posta ayarları
EMAIL = 'mehmetmac49@gmail.com'
EMAIL_PASSWORD = 'ytec enxo wmhj ikch'

db = SQLAlchemy(app)
jwt = JWTManager(app)

def get_emails_imap():
    try:
        print("IMAP bağlantısı başlatılıyor...")
        # Gmail IMAP sunucusuna bağlan
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        print("IMAP sunucusuna bağlandı, giriş yapılıyor...")
        mail.login(EMAIL, EMAIL_PASSWORD)
        print("Giriş başarılı, gelen kutusu seçiliyor...")
        mail.select("inbox")

        # Son 10 e-postayı al
        print("E-postalar aranıyor...")
        _, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        last_ten_emails = email_ids[-10:]  # Son 10 e-posta
        print(f"Bulunan e-posta sayısı: {len(last_ten_emails)}")

        emails = []
        for email_id in last_ten_emails:
            print(f"E-posta işleniyor: {email_id}")
            _, msg_data = mail.fetch(email_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # E-posta başlığını decode et
            subject = decode_header(msg["subject"])[0]
            if isinstance(subject[0], bytes):
                subject = subject[0].decode(subject[1] or 'utf-8')
            else:
                subject = subject[0]

            # Gönderen bilgisini decode et
            from_ = decode_header(msg["from"])[0]
            if isinstance(from_[0], bytes):
                from_ = from_[0].decode(from_[1] or 'utf-8')
            else:
                from_ = from_[0]

            # Tarih bilgisini al
            date = msg["date"]

            emails.append({
                'subject': subject,
                'sender': from_,
                'date': date
            })
            print(f"E-posta eklendi: {subject}")

        mail.close()
        mail.logout()
        print(f"Toplam {len(emails)} e-posta başarıyla alındı")
        return emails
    except Exception as e:
        print(f"E-posta alma hatası: {str(e)}")
        print(f"Hata türü: {type(e)}")
        import traceback
        print(f"Hata detayı: {traceback.format_exc()}")
        return []

# Kullanıcı modeli
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(20), nullable=False)
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

# Sohbet geçmişi için yeni model
class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    context = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'response': self.response,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context
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

# Veritabanını yeniden oluştur
with app.app_context():
    db.drop_all()  # Tüm tabloları sil
    db.create_all()  # Tabloları yeniden oluştur

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
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    try:
        # Örnek hava durumu verisi
        weather_data = {
            'temperature': 23,
            'description': 'Güneşli',
            'icon': '☀️'
        }
        return jsonify(weather_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Hatırlatıcılar endpoint'i
@app.route('/api/reminders', methods=['GET'])
@jwt_required()
def get_reminders():
    try:
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# E-postalar endpoint'i
@app.route('/api/emails', methods=['GET'])
@jwt_required()
def get_emails():
    try:
        print("E-posta endpoint'i çağrıldı")
        emails = get_emails_imap()
        print(f"Dönen e-posta sayısı: {len(emails)}")
        return jsonify(emails)
    except Exception as e:
        print(f"E-posta alma hatası: {str(e)}")
        return jsonify({'error': 'E-postalar alınamadı'}), 500

# Haberler endpoint'i
@app.route('/api/news', methods=['GET'])
@jwt_required()
def get_news():
    try:
        # Türkiye'den güncel haberler
        url = f'https://newsapi.org/v2/top-headlines?country=tr&apiKey={NEWS_API_KEY}'
        response = requests.get(url)
        data = response.json()
        
        if data['status'] == 'ok':
            news = []
            for article in data['articles'][:10]:  # İlk 10 haber
                news.append({
                    'title': article['title'],
                    'description': article['description'],
                    'source': article['source']['name'],
                    'url': article['url'],
                    'publishedAt': article['publishedAt'],
                    'imageUrl': article['urlToImage']
                })
            return jsonify(news)
        else:
            return jsonify({'error': 'Haberler alınamadı'}), 500
    except Exception as e:
        print(f"Haber alma hatası: {str(e)}")
        return jsonify({'error': 'Haberler alınamadı'}), 500

# Notlar endpoint'i
@app.route('/api/notes', methods=['GET'])
@jwt_required()
def get_notes():
    try:
        user_id = get_jwt_identity()
        notes = Note.query.filter_by(user_id=user_id).order_by(Note.created_at.desc()).all()
        return jsonify([note.to_dict() for note in notes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Not ekleme endpoint'i
@app.route('/api/notes', methods=['POST'])
@jwt_required()
def add_note():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'Not içeriği gerekli'}), 400
            
        note = Note(
            content=data['content'],
            user_id=user_id
        )
        
        db.session.add(note)
        db.session.commit()
        
        return jsonify(note.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

# Sohbet yanıtları için yardımcı fonksiyonlar
def get_greeting_response():
    greetings = [
        "Merhaba! Size nasıl yardımcı olabilirim?",
        "Hoş geldiniz! Bugün size nasıl yardımcı olabilirim?",
        "Merhaba! Sizinle sohbet etmekten mutluluk duyarım.",
        "Selam! Size nasıl yardımcı olabilirim?"
    ]
    return random.choice(greetings)

def get_weather_response():
    return "Hava durumu bilgisini kontrol ediyorum. Şu an için hava durumu bilgisi: Güneşli ve 23°C."

def get_time_response():
    current_time = datetime.now().strftime('%H:%M:%S')
    return f"Şu anki saat: {current_time}"

def get_date_response():
    current_date = datetime.now().strftime('%d/%m/%Y')
    return f"Bugünün tarihi: {current_date}"

def get_help_response():
    return """Size şu konularda yardımcı olabilirim:

1. Genel sohbet ve sorular
2. Hava durumu bilgisi
3. Saat ve tarih bilgisi
4. Hatırlatıcı oluşturma
5. Not alma
6. Haberleri görüntüleme
7. E-posta kontrolü
8. Matematiksel işlemler
9. Çeviri yapma
10. Güncel bilgiler

Nasıl yardımcı olabilirim?"""

def get_math_response(message):
    try:
        # Basit matematiksel işlemleri çözme
        expression = message.lower().replace('hesapla', '').replace('hesaplama', '').strip()
        result = eval(expression)
        return f"Sonuç: {result}"
    except:
        return "Üzgünüm, bu matematiksel işlemi çözemiyorum."

def get_translation_response(message):
    # Basit çeviri örneği (gerçek uygulamada bir çeviri API'si kullanılmalı)
    words = {
        'hello': 'merhaba',
        'goodbye': 'hoşça kal',
        'thank you': 'teşekkür ederim',
        'how are you': 'nasılsın'
    }
    
    for eng, tr in words.items():
        if eng in message.lower():
            return f"'{eng}' kelimesinin Türkçe karşılığı: '{tr}'"
    
    return "Üzgünüm, bu kelimeyi çeviremiyorum."

def get_context_aware_response(message, context):
    # Bağlama duyarlı yanıtlar
    if context and 'hava' in context.lower():
        return "Hava durumu hakkında başka bir sorunuz var mı?"
    elif context and 'saat' in context.lower():
        return "Saat ile ilgili başka bir sorunuz var mı?"
    return None

@app.route('/api/chat', methods=['POST'])
@jwt_required()
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        user_id = get_jwt_identity()
        
        # Son sohbet geçmişini al
        last_chat = ChatHistory.query.filter_by(user_id=user_id).order_by(ChatHistory.timestamp.desc()).first()
        context = last_chat.context if last_chat else None
        
        # Mesajı analiz et ve uygun yanıtı belirle
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['merhaba', 'selam', 'hey']):
            response = get_greeting_response()
        elif 'hava' in message_lower:
            response = get_weather_response()
        elif 'saat' in message_lower:
            response = get_time_response()
        elif 'tarih' in message_lower:
            response = get_date_response()
        elif 'yardım' in message_lower:
            response = get_help_response()
        elif 'hesapla' in message_lower or 'hesaplama' in message_lower:
            response = get_math_response(user_message)
        elif 'çevir' in message_lower or 'translation' in message_lower:
            response = get_translation_response(user_message)
        else:
            # Bağlama duyarlı yanıt kontrolü
            context_response = get_context_aware_response(user_message, context)
            if context_response:
                response = context_response
            else:
                response = "Üzgünüm, bu konuda size yardımcı olamıyorum. Başka bir soru sorabilir misiniz?"

        # Sohbet geçmişini kaydet
        chat_history = ChatHistory(
            user_id=user_id,
            message=user_message,
            response=response,
            context=user_message  # Basit bağlam takibi için mesajı sakla
        )
        db.session.add(chat_history)
        db.session.commit()

        return jsonify({
            'response': response,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'context': user_message
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 