import React from 'react';
import './App.css';
import Chat from './components/Chat';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Kişisel Asistan</h1>
      </header>
      <main className="App-main">
        <div className="left-panel">
          <Dashboard />
        </div>
        <div className="right-panel">
          <Chat />
        </div>
      </main>
    </div>
  );
}

export default App; 