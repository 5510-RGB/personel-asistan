import React from 'react';
import './App.css';
import Weather from './components/Weather/Weather';
import News from './components/News/News';
import Email from './components/Email/Email';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Kişisel Asistan</h1>
      </header>
      <main className="App-main">
        <Weather />
        <News />
        <Email />
      </main>
    </div>
  );
}

export default App; 