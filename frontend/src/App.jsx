import React, { useState } from 'react';
import Tuner from './components/Tuner';
import UserTracks from './components/UserTracks';
import TrackPage from './components/TrackPage';
import AdminComments from './components/AdminComments';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('tuner');
  const [user, setUser] = useState(null);
  const [currentTrackId, setCurrentTrackId] = useState(null);
  const token = localStorage.getItem('user_token');

  // Check user info on mount and token changes
  React.useEffect(() => {
    if (token) {
      fetch('http://localhost:8002/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => setUser(data))
        .catch(() => setUser(null));
    } else {
      setUser(null);
    }
  }, [token]);

  const handleOpenTrackPage = (trackId) => {
    setCurrentTrackId(trackId);
    setActiveTab('track-page');
  };

  const handleBackFromTrackPage = () => {
    setCurrentTrackId(null);
    setActiveTab('user');
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">🎸 Guitar Pro</h1>
        <nav className="app-nav">
          {activeTab !== 'track-page' && (
            <>
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
              {user && user.is_admin && (
                <button
                  className={`nav-button ${activeTab === 'admin' ? 'active' : ''}`}
                  onClick={() => setActiveTab('admin')}
                >
                  🛡️ Admin
                </button>
              )}
            </>
          )}
        </nav>
      </header>

      <main className="app-main">
        {activeTab === 'tuner' && <Tuner />}
        {activeTab === 'user' && <UserTracks onOpenTrackPage={handleOpenTrackPage} />}
        {activeTab === 'track-page' && currentTrackId && (
          <TrackPage trackId={currentTrackId} token={token} onBack={handleBackFromTrackPage} />
        )}
        {activeTab === 'admin' && user && user.is_admin && <AdminComments token={token} />}
      </main>
    </div>
  );
}

export default App;