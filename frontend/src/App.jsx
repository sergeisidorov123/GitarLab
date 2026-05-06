import React, { useState } from 'react';
import Tuner from './components/Tuner';
import SongCatalog from './components/SongCatalog';
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
            className={`nav-button ${activeTab === 'catalog' ? 'active' : ''}`}
            onClick={() => setActiveTab('catalog')}
          >
            📚 Song Catalog
          </button>
        </nav>
      </header>

      <main className="app-main">
        {activeTab === 'tuner' && <Tuner />}
        {activeTab === 'catalog' && <SongCatalog />}
      </main>
    </div>
  );
}

export default App;