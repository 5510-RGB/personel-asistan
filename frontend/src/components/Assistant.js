import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaPaperPlane, FaBell, FaEnvelope, FaNewspaper, FaStickyNote, FaClock, FaUser, FaPlus, FaSun, FaMoon } from 'react-icons/fa';

const Assistant = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [weather, setWeather] = useState(null);
  const [reminders, setReminders] = useState([]);
  const [emails, setEmails] = useState([]);
  const [news, setNews] = useState([]);
  const [showReminders, setShowReminders] = useState(false);
  const [showEmails, setShowEmails] = useState(false);
  const [showNews, setShowNews] = useState(false);
  const [newReminder, setNewReminder] = useState({ title: '', time: '' });
  const [notes, setNotes] = useState([]);
  const [newNote, setNewNote] = useState('');
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');

  useEffect(() => {
    if (theme === 'dark') {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUserInfo();
      fetchNotes();
    }

    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    fetchWeather();
    fetchReminders();
    fetchEmails();
    fetchNews();

    return () => clearInterval(timer);
  }, []);

  const fetchUserInfo = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/auth/me');
      setUser(response.data);
    } catch (error) {
      console.error('Kullanıcı bilgileri alınamadı:', error);
    }
  };

  const fetchWeather = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/weather');
      setWeather(response.data);
    } catch (error) {
      console.error('Hava durumu alınamadı:', error);
    }
  };

  const fetchReminders = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/reminders');
      setReminders(response.data);
    } catch (error) {
      console.error('Hatırlatıcılar alınamadı:', error);
    }
  };

  const fetchEmails = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/emails');
      setEmails(response.data);
    } catch (error) {
      console.error('E-postalar alınamadı:', error);
    }
  };

  const fetchNews = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/news');
      setNews(response.data);
    } catch (error) {
      console.error('Haberler alınamadı:', error);
    }
  };

  const fetchNotes = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/notes');
      setNotes(response.data);
    } catch (error) {
      console.error('Notlar alınamadı:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    setLoading(true);
    const userMessage = inputMessage;
    setInputMessage('');

    setMessages(prev => [...prev, { content: userMessage, sender: 'user' }]);

    try {
      const response = await axios.post('http://127.0.0.1:5000/api/chat', {
        message: userMessage
      });

      setMessages(prev => [...prev, { content: response.data.response, sender: 'assistant' }]);
    } catch (error) {
      console.error('Mesaj gönderme hatası:', error);
      setMessages(prev => [...prev, { content: 'Üzgünüm, bir hata oluştu.', sender: 'assistant' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddReminder = async (e) => {
    e.preventDefault();
    if (!newReminder.title || !newReminder.time) {
      console.log("Hatırlatıcı başlığı ve zamanı gerekli.");
      return;
    }
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/reminders', newReminder);
      setReminders(prev => [...prev, response.data]);
      setNewReminder({ title: '', time: '' });
      setShowReminders(false);
      console.log("Hatırlatıcı başarıyla eklendi:", response.data);
    } catch (error) {
      console.error('Hatırlatıcı eklenemedi:', error.response ? error.response.data : error.message);
    }
  };

  const handleAddNote = async (e) => {
    e.preventDefault();
    if (!newNote.trim()) {
      console.log("Not içeriği boş olamaz.");
      return;
    }
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/notes', {
        content: newNote
      });
      setNotes(prev => [...prev, response.data]);
      setNewNote('');
      console.log("Not başarıyla eklendi:", response.data);
    } catch (error) {
      console.error('Not eklenemedi:', error.response ? error.response.data : error.message);
    }
  };

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'bg-gray-800 text-gray-200' : 'bg-gray-100 text-gray-900'}`}>
      <div className={`shadow-md ${theme === 'dark' ? 'bg-gray-900 text-white' : 'bg-white text-gray-900'}`}>
        <div className="max-w-6xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center overflow-hidden">
                <img
                  src="https://generative-ai-frontend-dot-cursor-code-ai.uc.r.appspot.com/image/786c016d-88b1-4581-a3e3-4f9c701c8993.jpg"
                  alt="Asistan"
                  className="w-full h-full object-cover"
                />
              </div>
              <div>
                <h2 className="font-bold">{user?.username || 'Kullanıcı'}</h2>
                <p className="text-sm text-gray-600">{user?.email || ''}</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={toggleTheme}
                className="flex items-center space-x-2 bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600"
              >
                {theme === 'light' ? <FaMoon /> : <FaSun />}
                <span>Tema</span>
              </button>

              <button
                onClick={() => setShowReminders(!showReminders)}
                className="flex items-center space-x-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
              >
                <FaBell />
                <span>Hatırlatıcılar</span>
              </button>
              <button
                onClick={() => setShowEmails(!showEmails)}
                className="flex items-center space-x-2 bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600"
              >
                <FaEnvelope />
                <span>E-postalar</span>
              </button>
              <button
                onClick={() => setShowNews(!showNews)}
                className="flex items-center space-x-2 bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600"
              >
                <FaNewspaper />
                <span>Haberler</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className={`md:col-span-2 rounded-lg shadow p-4 ${theme === 'dark' ? 'bg-gray-900 text-gray-200' : 'bg-white text-gray-900'}`}>
            <div className="flex items-center mb-4">
              <img
                src="https://generative-ai-frontend-dot-cursor-code-ai.uc.r.appspot.com/image/786c016d-88b1-4581-a3e3-4f9c701c8993.jpg"
                alt="Asistan"
                className="w-10 h-10 rounded-full mr-3"
              />
              <h2 className="text-xl font-bold">Yapay Zeka Asistanı</h2>
            </div>

            <div className="h-[450px] overflow-y-auto mb-4 space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] rounded-lg p-3 ${
                      message.sender === 'user'
                         ? (theme === 'dark' ? 'bg-blue-700 text-white' : 'bg-blue-500 text-white')
                         : (theme === 'dark' ? 'bg-gray-700 text-gray-200' : 'bg-gray-200 text-gray-800')
                    }`}
                  >
                    {message.content}
                  </div>
                </div>
              ))}
            </div>

            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Mesajınızı yazın..."
                className={`flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-gray-200 focus:ring-blue-700' : 'bg-white border-gray-300 text-gray-900 focus:ring-blue-500'}`}
              />
              <button
                type="submit"
                disabled={loading}
                className={`p-2 rounded-lg focus:outline-none focus:ring-2 ${loading ? 'opacity-50 cursor-not-allowed' : ''} ${theme === 'dark' ? 'bg-blue-700 text-white hover:bg-blue-800 focus:ring-blue-700' : 'bg-blue-500 text-white hover:bg-blue-600 focus:ring-blue-500'}`}
              >
                <FaPaperPlane />
              </button>
            </form>
          </div>

          <div className="space-y-4">
            {showReminders && (
              <div className={`rounded-lg shadow p-4 ${theme === 'dark' ? 'bg-gray-900 text-gray-200' : 'bg-white text-gray-900'}`}>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold">Hatırlatıcılar</h3>
                  <button
                    onClick={() => setShowReminders(false)}
                    className={`text-gray-500 hover:text-gray-700 ${theme === 'dark' ? 'text-gray-400 hover:text-gray-200' : ''}`}
                  >
                    ✕
                  </button>
                </div>
                <form onSubmit={handleAddReminder} className="mb-4">
                  <input
                    type="text"
                    value={newReminder.title}
                    onChange={(e) => setNewReminder({...newReminder, title: e.target.value})}
                    placeholder="Hatırlatıcı başlığı"
                    className={`w-full p-2 border rounded mb-2 ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-gray-200 placeholder-gray-400' : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'}`}
                  />
                  <input
                    type="time"
                    value={newReminder.time}
                    onChange={(e) => setNewReminder({...newReminder, time: e.target.value})}
                    className={`w-full p-2 border rounded mb-2 ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-gray-200' : 'bg-white border-gray-300 text-gray-900'}`}
                  />
                  <button type="submit" className={`w-full p-2 rounded ${theme === 'dark' ? 'bg-blue-700 text-white hover:bg-blue-800' : 'bg-blue-500 text-white hover:bg-blue-600'}`}>
                    Ekle
                  </button>
                </form>
                <div className="space-y-2">
                  {reminders.map((reminder, index) => (
                    <div key={index} className={`flex justify-between items-center p-2 rounded ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'}`}>
                      <span>{reminder.title}</span>
                      <span>{reminder.time}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {showEmails && (
              <div className={`rounded-lg shadow p-4 ${theme === 'dark' ? 'bg-gray-900 text-gray-200' : 'bg-white text-gray-900'}`}>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold">E-postalar</h3>
                  <button
                    onClick={() => setShowEmails(false)}
                    className={`text-gray-500 hover:text-gray-700 ${theme === 'dark' ? 'text-gray-400 hover:text-gray-200' : ''}`}
                  >
                    ✕
                  </button>
                </div>
                <div className="space-y-2">
                  {emails.map((email, index) => (
                    <div key={index} className={`p-2 rounded ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'}`}>
                      <p className="font-bold">{email.subject}</p>
                      <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>{email.sender}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {showNews && (
              <div className={`rounded-lg shadow p-4 ${theme === 'dark' ? 'bg-gray-900 text-gray-200' : 'bg-white text-gray-900'}`}>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold">Haberler</h3>
                  <button
                    onClick={() => setShowNews(false)}
                    className={`text-gray-500 hover:text-gray-700 ${theme === 'dark' ? 'text-gray-400 hover:text-gray-200' : ''}`}
                  >
                    ✕
                  </button>
                </div>
                <div className="space-y-2">
                  {news.map((item, index) => (
                    <div key={index} className={`p-2 rounded ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'}`}>
                      <p className="font-bold">{item.title}</p>
                      <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>{item.source}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className={`rounded-lg shadow p-4 ${theme === 'dark' ? 'bg-gray-900 text-gray-200' : 'bg-white text-gray-900'}`}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold">Notlar</h3>
                <button
                  onClick={() => setNewNote('')}
                  className={`text-blue-500 hover:text-blue-700 ${theme === 'dark' ? 'text-blue-400 hover:text-blue-500' : ''}`}
                >
                  <FaPlus />
                </button>
              </div>
              <form onSubmit={handleAddNote} className="mb-4">
                <textarea
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  placeholder="Yeni not ekle..."
                  className={`w-full p-2 border rounded mb-2 ${theme === 'dark' ? 'bg-gray-700 border-gray-600 text-gray-200 placeholder-gray-400' : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'}`}
                  rows="3"
                />
                <button type="submit" className={`w-full p-2 rounded ${theme === 'dark' ? 'bg-blue-700 text-white hover:bg-blue-800' : 'bg-blue-500 text-white hover:bg-blue-600'}`}>
                  Not Ekle
                </button>
              </form>
              <div className="space-y-2">
                {notes.slice().reverse().map((note, index) => (
                  <div key={index} className={`p-2 rounded ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'}`}>
                    <p>{note.content}</p>
                    <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
                      {new Date(note.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Assistant; 