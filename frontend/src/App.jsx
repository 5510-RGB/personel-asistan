import React from 'react';
import './App.css';
import Chat from './components/Chat/Chat';
import Dashboard from './components/Dashboard/Dashboard';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Kişisel Asistan</h1>
      </header>
      <main className="App-main">
        <Dashboard />
        <Chat />
      </main>
    </div>
  );
}

export default App; 