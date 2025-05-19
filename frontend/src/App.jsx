import React, { useState, useRef, useEffect } from 'react';
import './App.css';
import { getWeatherData } from './services/weatherService';
import { getCalendarEvents } from './services/calendarService';

function App() {
  const [activePanel, setActivePanel] = useState(null);
  const [notes, setNotes] = useState([]);
  const [newNote, setNewNote] = useState('');
  const [messages, setMessages] = useState([
    { id: 1, text: 'Merhaba! Size nasıl yardımcı olabilirim?', sender: 'assistant' }
  ]);
  const [newMessage, setNewMessage] = useState('');
  const [weatherData, setWeatherData] = useState({
    temperature: 19,
    condition: 'Parçalı bulutlu',
    humidity: 65,
    windSpeed: 10
  });
  const [calendarEvents, setCalendarEvents] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Hava durumu ve takvim verilerini güncelle
  useEffect(() => {
    const updateData = async () => {
      const weather = await getWeatherData();
      const events = await getCalendarEvents();
      setWeatherData(weather);
      setCalendarEvents(events);
    };

    updateData();
    // Her 5 dakikada bir güncelle
    const interval = setInterval(updateData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const handleAddNote = () => {
    if (newNote.trim()) {
      setNotes([...notes, { id: Date.now(), content: newNote }]);
      setNewNote('');
      setActivePanel(null);
    }
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (newMessage.trim()) {
      // Kullanıcı mesajını ekle
      const userMessage = {
        id: Date.now(),
        text: newMessage,
        sender: 'user'
      };
      setMessages(prev => [...prev, userMessage]);
      setNewMessage('');

      // Asistan yanıtını simüle et
      setTimeout(() => {
        const assistantMessage = {
          id: Date.now() + 1,
          text: getAssistantResponse(newMessage),
          sender: 'assistant'
        };
        setMessages(prev => [...prev, assistantMessage]);
      }, 1000);
    }
  };

  const getAssistantResponse = (message) => {
    // Basit yanıt mantığı
    const lowerMessage = message.toLowerCase();
    if (lowerMessage.includes('merhaba') || lowerMessage.includes('selam')) {
      return 'Merhaba! Size nasıl yardımcı olabilirim?';
    } else if (lowerMessage.includes('nasılsın')) {
      return 'Ben bir yapay zeka asistanıyım, her zaman yardımcı olmaya hazırım!';
    } else if (lowerMessage.includes('saat kaç')) {
      const now = new Date();
      return `Şu an saat: ${now.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}`;
    } else if (lowerMessage.includes('günlerden ne')) {
      const days = ['Pazar', 'Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi'];
      const today = new Date();
      return `Bugün ${days[today.getDay()]}.`;
    } else if (lowerMessage.includes('şaka')) {
      return "Tabii! Neden bilgisayarlar asla üşümez? Çünkü her zaman bir 'fan'ları vardır!";
    } else if (lowerMessage.includes('yardım')) {
      return 'Size nasıl yardımcı olabilirim? Takvim, not, hava durumu gibi konularda sorular sorabilirsiniz.';
    } else if (lowerMessage.includes('kimsin')) {
      return 'Ben senin kişisel asistanınım. Günlük işlerini kolaylaştırmak için buradayım.';
    } else if (lowerMessage.includes('hangi dilleri konuşuyorsun')) {
      return 'Şu anda Türkçe ve İngilizce olarak yardımcı olabilirim.';
    } else if (lowerMessage.includes('hava nasıl olacak')) {
      return 'Hava durumu panelinden güncel bilgilere ulaşabilirsin.';
    } else if (lowerMessage.includes('hava durumu')) {
      return 'Bugün hava 19°C ve parçalı bulutlu.';
    } else if (lowerMessage.includes('toplantı')) {
      return 'Bugün saat 14:00\'te bir toplantınız var.';
    } else if (lowerMessage.includes('not')) {
      return 'Notlarınızı görüntülemek için notlar paneline gidebilirsiniz.';
    } else if (lowerMessage.includes('teşekkür') || lowerMessage.includes('teşekkürler')) {
      return 'Rica ederim! Yardımcı olabildiysem ne mutlu bana.';
    } else {
      return 'Üzgünüm, bu konuda size yardımcı olamıyorum. Başka bir konuda yardıma ihtiyacınız var mı?';
    }
  };

  return (
    <div className="assistant-container">
      <div className="profile-section">
        <img src="/assistant-profile.jpg" alt="Profil" className="profile-img assistant-profile-img" />
        <h1 className="welcome-text">Merhaba, size nasıl yardımcı olabilirim?</h1>
      </div>
      <div className="grid">
        <div className="card" onClick={() => setActivePanel('calendar')}>
          <span className="icon" role="img" aria-label="Takvim">📅</span>
          <div className="card-title">Takvim</div>
          <div className="card-desc">
            {calendarEvents.length > 0 
              ? `Bugün ${calendarEvents.length} etkinlik var`
              : 'Bugün etkinlik yok'}
          </div>
        </div>
        <div className="card" onClick={() => setActivePanel('weather')}>
          <span className="icon" role="img" aria-label="Hava Durumu">⛅</span>
          <div className="card-title">Hava Durumu</div>
          <div className="card-desc">{weatherData.temperature}° {weatherData.condition}</div>
        </div>
        <div className="card" onClick={() => setActivePanel('email')}>
          <span className="icon" role="img" aria-label="E-posta">📧</span>
          <div className="card-title">E-posta</div>
          <div className="card-desc">Yeni e-posta var</div>
        </div>
        <div className="card" onClick={() => setActivePanel('notes')}>
          <span className="icon" role="img" aria-label="Notlar">📝</span>
          <div className="card-title">Notlar</div>
          <div className="card-desc">{notes.length} not</div>
        </div>
        <div className="card" onClick={() => setActivePanel('chat')}>
          <span className="icon" role="img" aria-label="Sohbet">💬</span>
          <div className="card-title">Sohbet</div>
          <div className="card-desc">Merhaba!</div>
        </div>
        <div className="card" onClick={() => setActivePanel('createNote')}>
          <span className="icon" role="img" aria-label="Not Oluştur">🎤</span>
          <div className="card-title">Not oluştur</div>
        </div>
      </div>

      {/* Paneller */}
      {activePanel === 'chat' && (
        <div className="modal">
          <div className="modal-content">
            <button className="close-btn" onClick={() => setActivePanel(null)}>Kapat</button>
            <h2>Sohbet</h2>
            <div className="chat-box">
              <div className="messages-container">
                {messages.map((message) => (
                  <div key={message.id} className={`message ${message.sender}`}>
                    {message.text}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
              <form onSubmit={handleSendMessage} className="chat-input-form">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Bir mesaj yazın..."
                  className="chat-input"
                />
                <button type="submit" className="send-btn">Gönder</button>
              </form>
            </div>
          </div>
        </div>
      )}

      {activePanel === 'calendar' && (
        <div className="modal">
          <div className="modal-content">
            <button className="close-btn" onClick={() => setActivePanel(null)}>Kapat</button>
            <h2>Takvim</h2>
            <div className="calendar-content">
              {calendarEvents.map(event => (
                <div key={event.id} className="event-card">
                  <h3>{event.title}</h3>
                  <p>Saat: {event.startTime.toLocaleTimeString()}</p>
                  <p>Konum: {event.location}</p>
                  {event.description && <p className="event-description">{event.description}</p>}
                </div>
              ))}
              {calendarEvents.length === 0 && (
                <p className="no-events">Bugün için planlanmış etkinlik bulunmuyor.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {activePanel === 'weather' && (
        <div className="modal">
          <div className="modal-content">
            <button className="close-btn" onClick={() => setActivePanel(null)}>Kapat</button>
            <h2>Hava Durumu</h2>
            <div className="weather-content">
              <div className="weather-card">
                <div className="temperature">{weatherData.temperature}°C</div>
                <div className="condition">{weatherData.condition}</div>
                <div className="details">
                  <span>Nem: {weatherData.humidity}%</span>
                  <span>Rüzgar: {weatherData.windSpeed} km/s</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activePanel === 'email' && (
        <div className="modal">
          <div className="modal-content">
            <button className="close-btn" onClick={() => setActivePanel(null)}>Kapat</button>
            <h2>E-posta</h2>
            <div className="email-content">
              <div className="email-list">
                <div className="email-item">
                  <div className="email-header">
                    <span className="sender">Ahmet Yılmaz</span>
                    <span className="date">10:30</span>
                  </div>
                  <div className="subject">Proje Güncellemesi</div>
                  <div className="preview">Merhaba, projenin son durumu hakkında...</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activePanel === 'notes' && (
        <div className="modal">
          <div className="modal-content">
            <button className="close-btn" onClick={() => setActivePanel(null)}>Kapat</button>
            <h2>Notlar</h2>
            <div className="notes-content">
              {notes.map(note => (
                <div key={note.id} className="note-item">
                  <p>{note.content}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activePanel === 'createNote' && (
        <div className="modal">
          <div className="modal-content">
            <button className="close-btn" onClick={() => setActivePanel(null)}>Kapat</button>
            <h2>Not Oluştur</h2>
            <div className="create-note-content">
              <textarea
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                placeholder="Notunuzu buraya yazın..."
                rows="4"
              />
              <button onClick={handleAddNote} className="save-btn">Kaydet</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App; 