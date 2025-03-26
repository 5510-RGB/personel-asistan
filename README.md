# Yapay Zeka Destekli Kişisel Asistan

## Proje Tanımı
Bu proje, kullanıcıların günlük hayatlarını kolaylaştırmak için tasarlanmış yapay zeka destekli bir kişisel asistandır. Sesli ve yazılı komutlarla çalışan bu asistan, takvim yönetimi, hatırlatıcılar, hava durumu bilgisi, e-posta yönetimi, web arama ve haber takibi gibi işlevleri yerine getirir.

## Hedef Kitle
- Bireysel Kullanıcılar
- Profesyoneller
- Teknoloji Meraklıları

## Temel Özellikler
1. Sesli Komut ve NLP (Doğal Dil İşleme)
2. Hatırlatıcılar ve Takvim Yönetimi
3. Hava Durumu ve Haber Bilgisi
4. E-posta Yönetimi
5. Web Arama ve Bilgi Sorgulama
6. Makine Öğrenmesi ile Kişiselleştirme

## Teknoloji Yığını
- Backend: Python (Flask)
- Frontend: React (Web) ve Electron.js (Masaüstü)
- Veritabanı: PostgreSQL
- Ses Tanıma: OpenAI Whisper
- NLP: OpenAI GPT
- Entegrasyonlar: Google Calendar API, Weather API, Gmail API

## Proje Yapısı
```
personal-assistant/
├── backend/                 # Flask backend
│   ├── api/                # API endpoints
│   ├── core/               # Core functionality
│   ├── models/             # Database models
│   └── services/           # External service integrations
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── services/      # API services
│   │   └── utils/         # Utility functions
│   └── public/            # Static files
├── desktop/               # Electron desktop app
│   ├── src/              # Desktop app source
│   └── main.js           # Electron main process
└── docs/                 # Project documentation
```

## Kurulum
1. Backend kurulumu:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Frontend kurulumu:
```bash
cd frontend
npm install
```

3. Desktop uygulaması kurulumu:
```bash
cd desktop
npm install
```

## Geliştirme
1. Backend'i başlatmak için:
```bash
cd backend
flask run
```

2. Frontend'i başlatmak için:
```bash
cd frontend
npm start
```

3. Desktop uygulamasını başlatmak için:
```bash
cd desktop
npm start
```

mkdir -p backend/api backend/core backend/models backend/services
mkdir -p frontend/src/components frontend/src/services frontend/src/utils frontend/public
mkdir -p desktop/src
mkdir -p docs 