import React, { useState } from 'react';
import './Chat.css';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      const newMessage = { content: input, sender: 'user' };
      setMessages([...messages, newMessage]);
      setInput('');
      
      // Asistan yanıtı
      setTimeout(() => {
        setMessages(prev => [...prev, {
          content: 'Size nasıl yardımcı olabilirim?',
          sender: 'assistant'
        }]);
      }, 500);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender}`}>
            {message.content}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Bir mesaj yazın..."
        />
        <button type="submit">Gönder</button>
      </form>
    </div>
  );
}

export default Chat; 