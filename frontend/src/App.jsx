import React, { useState } from 'react';
import Tuner from './components/Tuner';
import UserTracks from './components/UserTracks';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('tuner');

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">🎸 Guitar Pro</h1>
        <nav className="app-nav">
          <button
            className={`nav-button ${activeTab === 'tuner' ? 'active' : ''}`}
            onClick={() => setActiveTab('tuner')}
          >
            🎵 Tuner
          </button>
          <button
            className={`nav-button ${activeTab === 'user' ? 'active' : ''}`}
            onClick={() => setActiveTab('user')}
          >
            🎧 Tuning Library
          </button>
        </nav>
      </header>

      <main className="app-main">
        {activeTab === 'tuner' && <Tuner />}
        {activeTab === 'user' && <UserTracks />}
      </main>
    </div>
  );
}

export default App;