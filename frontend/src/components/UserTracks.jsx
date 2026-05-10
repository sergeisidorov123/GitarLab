import React, { useEffect, useState } from 'react';

const API_URL = 'http://localhost:8002';
const CATALOG_API_URL = 'http://localhost:8001';

const TUNING_PRESETS = {
  standard: { name: 'Standard (E A D G B E)', strings: ['E', 'A', 'D', 'G', 'B', 'E'], frequencies: [82.41, 110.00, 146.83, 196.00, 246.94, 329.63] },
  drop_d: { name: 'Drop D (D A D G B E)', strings: ['D', 'A', 'D', 'G', 'B', 'E'], frequencies: [73.42, 110.00, 146.83, 196.00, 246.94, 329.63] },
  half_step_down: { name: 'Half Step Down', strings: ['D#', 'G#', 'C#', 'F#', 'A#', 'D#'], frequencies: [77.78, 103.83, 138.59, 185.00, 233.08, 311.13] },
  full_step_down: { name: 'Full Step Down (D G C F A D)', strings: ['D', 'G', 'C', 'F', 'A', 'D'], frequencies: [73.42, 98.00, 130.81, 174.61, 220.00, 293.66] },
  open_g: { name: 'Open G (D G D G B D)', strings: ['D', 'G', 'D', 'G', 'B', 'D'], frequencies: [73.42, 98.00, 146.83, 196.00, 246.94, 293.66] },
  open_e: { name: 'Open E (E B E G# B E)', strings: ['E', 'B', 'E', 'G#', 'B', 'E'], frequencies: [82.41, 123.47, 164.81, 207.65, 246.94, 329.63] },
  open_d: { name: 'Open D (D A D F# A D)', strings: ['D', 'A', 'D', 'F#', 'A', 'D'], frequencies: [73.42, 110.00, 146.83, 185.00, 220.00, 293.66] },
};

const getTuningDisplayName = (tuningName, apiTunings) => {
  // First check if it's a preset key
  if (TUNING_PRESETS[tuningName]) {
    return TUNING_PRESETS[tuningName].name;
  }
  // Then check if it matches an API tuning name
  const apiTuning = apiTunings.find(t => t.name === tuningName);
  if (apiTuning) {
    return apiTuning.name;
  }
  // Fallback to the raw name
  return tuningName;
};

const UserTracks = ({ onOpenTrackPage }) => {
  const [token, setToken] = useState(localStorage.getItem('user_token') || '');
  const [username, setUsername] = useState(localStorage.getItem('user_name') || '');
  const [mode, setMode] = useState('login');
  const [authForm, setAuthForm] = useState({ username: '', password: '' });
  const [trackForm, setTrackForm] = useState({
    title: '',
    artist: '',
    tuning_name: 'standard',
    string_names: TUNING_PRESETS.standard.strings,
    frequencies: TUNING_PRESETS.standard.frequencies,
    useCustom: false,
  });
  const [editingTrackId, setEditingTrackId] = useState(null);
  const [view, setView] = useState('all');
  const [search, setSearch] = useState('');
  const [tracks, setTracks] = useState([]);
  const [favoriteIds, setFavoriteIds] = useState(new Set());
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [apiTunings, setApiTunings] = useState([]);

  useEffect(() => {
    // Load tunings from catalog service
    fetch(`${CATALOG_API_URL}/tunings/`)
      .then(res => res.json())
      .then(data => setApiTunings(data))
      .catch(err => console.error('Failed to load tunings:', err));

    if (token) {
      loadTracks();
    } else {
      setTracks([]);
    }
  }, [token, view, search]);

  const authHeaders = () => {
    return token
      ? {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      : { 'Content-Type': 'application/json' };
  };

  const handleAuthChange = (event) => {
    const { name, value } = event.target;
    setAuthForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleTrackChange = (event) => {
    const { name, value } = event.target;
    if (name === 'tuning_name' && !trackForm.useCustom) {
      const preset = TUNING_PRESETS[value];
      if (preset) {
        setTrackForm((prev) => ({
          ...prev,
          [name]: value,
          string_names: preset.strings,
          frequencies: preset.frequencies,
        }));
      }
    } else if (name === 'string_names' || name === 'frequencies') {
      const values = value.split(',').map((v) => v.trim());
      if (name === 'frequencies') {
        setTrackForm((prev) => ({
          ...prev,
          [name]: values.map((v) => parseFloat(v) || 0),
        }));
      } else {
        setTrackForm((prev) => ({
          ...prev,
          [name]: values,
        }));
      }
    } else {
      setTrackForm((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleCustomTuningToggle = () => {
    setTrackForm((prev) => ({
      ...prev,
      useCustom: !prev.useCustom,
      tuning_name: prev.useCustom ? 'standard' : 'custom',
    }));
  };

  const saveSession = (tokenValue, usernameValue) => {
    setToken(tokenValue);
    setUsername(usernameValue);
    localStorage.setItem('user_token', tokenValue);
    localStorage.setItem('user_name', usernameValue);
    setError(null);
  };

  const logout = () => {
    setToken('');
    setUsername('');
    localStorage.removeItem('user_token');
    localStorage.removeItem('user_name');
    setTracks([]);
  };

  const login = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify(authForm),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Invalid credentials');
      }
      saveSession(data.access_token, data.username);
      setAuthForm({ username: '', password: '' });
      setView('all');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const register = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify(authForm),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed');
      }
      await login();
      setAuthForm({ username: '', password: '' });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadTracks = async () => {
    if (!token && view !== 'all') {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      let url = `${API_URL}/tracks`;
      if (view === 'my') url = `${API_URL}/tracks/my`;
      if (view === 'favorites') url = `${API_URL}/tracks/favorites`;
      if (search) url += `?search=${encodeURIComponent(search)}`;

      const response = await fetch(url, {
        headers: authHeaders(),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to load tracks');
      }
      setTracks(data);
      const favorites = new Set(data.filter((t) => t.is_favorite).map((t) => t.id));
      setFavoriteIds(favorites);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const saveTrack = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        title: trackForm.title,
        artist: trackForm.artist,
        tuning_name: trackForm.tuning_name,
        string_names: trackForm.string_names,
        frequencies: trackForm.frequencies,
      };

      const method = editingTrackId ? 'PUT' : 'POST';
      const url = editingTrackId ? `${API_URL}/tracks/${editingTrackId}` : `${API_URL}/tracks/`;

      const response = await fetch(url, {
        method,
        headers: authHeaders(),
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Could not save track');
      }
      resetTrackForm();
      loadTracks();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const resetTrackForm = () => {
    setTrackForm({
      title: '',
      artist: '',
      tuning_name: 'standard',
      string_names: TUNING_PRESETS.standard.strings,
      frequencies: TUNING_PRESETS.standard.frequencies,
      useCustom: false,
    });
    setEditingTrackId(null);
    setShowForm(false);
  };

  const editTrack = (track) => {
    const isPreset = track.tuning_name in TUNING_PRESETS;
    setTrackForm({
      title: track.title,
      artist: track.artist,
      tuning_name: track.tuning_name,
      string_names: track.string_names,
      frequencies: track.frequencies,
      useCustom: !isPreset,
    });
    setEditingTrackId(track.id);
    setShowForm(true);
  };

  const deleteTrack = async (trackId) => {
    if (!window.confirm('Are you sure you want to delete this track?')) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/tracks/${trackId}`, {
        method: 'DELETE',
        headers: authHeaders(),
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Could not delete track');
      }
      loadTracks();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleFavorite = async (trackId, isFavorite) => {
    setLoading(true);
    setError(null);
    try {
      const method = isFavorite ? 'DELETE' : 'POST';
      const response = await fetch(`${API_URL}/tracks/${trackId}/favorite`, {
        method,
        headers: authHeaders(),
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Action failed');
      }
      loadTracks();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="card">
        <h2 className="card-title">🎧 Tuning Library</h2>
        <p className="card-subtitle">Create and manage your guitar tuning presets.</p>

        {error && (
          <div className="error-message">
            <strong>⚠️ Error:</strong> {error}
          </div>
        )}

        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
          <button
            className={`btn ${mode === 'login' ? 'active' : ''}`}
            onClick={() => setMode('login')}
          >
            Sign In
          </button>
          <button
            className={`btn ${mode === 'register' ? 'active' : ''}`}
            onClick={() => setMode('register')}
          >
            Create Account
          </button>
        </div>

        <div style={{ display: 'grid', gap: '1rem', maxWidth: '400px' }}>
          <input
            type="text"
            name="username"
            placeholder="Username"
            value={authForm.username}
            onChange={handleAuthChange}
            style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ddd' }}
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={authForm.password}
            onChange={handleAuthChange}
            style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ddd' }}
          />
          <button
            className="btn"
            onClick={mode === 'login' ? login : register}
            disabled={loading}
          >
            {mode === 'login' ? 'Sign In' : 'Create Account'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
          <div>
            <h2 className="card-title">🎧 {username}'s Tuning Library</h2>
            <p className="card-subtitle">Manage your guitar tuning presets and collections</p>
          </div>
          <button className="btn btn-danger" onClick={logout}>
            Logout
          </button>
        </div>

        {error && (
          <div className="error-message">
            <strong>⚠️ Error:</strong> {error}
          </div>
        )}

        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
          {['all', 'my', 'favorites'].map((item) => (
            <button
              key={item}
              className={`btn ${view === item ? 'active' : ''}`}
              onClick={() => setView(item)}
            >
              {item === 'all' ? '🌐 All Tunings' : item === 'my' ? '📝 My Tunings' : '⭐ Favorites'}
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search title, artist, or tuning name..."
            style={{ flex: '1', minWidth: '200px', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ddd' }}
          />
          {view === 'my' && (
            <button className="btn" onClick={() => { setShowForm(!showForm); if (editingTrackId) resetTrackForm(); }}>
              {showForm ? '✕ Cancel' : '+ New Tuning'}
            </button>
          )}
        </div>

        {view === 'my' && showForm && (
          <div style={{ background: '#f9f9f9', padding: '1.5rem', borderRadius: '12px', marginBottom: '2rem' }}>
            <h3 style={{ marginTop: 0 }}>{editingTrackId ? 'Edit Tuning' : 'Create New Tuning'}</h3>
            <div style={{ display: 'grid', gap: '1rem' }}>
              <input
                type="text"
                name="title"
                value={trackForm.title}
                placeholder="Song title"
                onChange={handleTrackChange}
                style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ddd' }}
              />
              <input
                type="text"
                name="artist"
                value={trackForm.artist}
                placeholder="Artist name"
                onChange={handleTrackChange}
                style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ddd' }}
              />
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <input
                  type="checkbox"
                  checked={trackForm.useCustom}
                  onChange={handleCustomTuningToggle}
                  style={{ cursor: 'pointer' }}
                />
                <label style={{ cursor: 'pointer', flex: 1 }}>Use Custom Tuning</label>
              </div>
              {!trackForm.useCustom ? (
                <select
                  name="tuning_name"
                  value={trackForm.tuning_name}
                  onChange={handleTrackChange}
                  style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ddd' }}
                >
                  {Object.entries(TUNING_PRESETS).map(([key, preset]) => (
                    <option key={key} value={key}>
                      {preset.name}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  type="text"
                  name="tuning_name"
                  value={trackForm.tuning_name}
                  placeholder="Custom tuning name (e.g., DADGAD)"
                  onChange={handleTrackChange}
                  style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ddd' }}
                />
              )}
              {trackForm.useCustom && (
                <>
                  <input
                    type="text"
                    name="string_names"
                    value={trackForm.string_names.join(', ')}
                    placeholder="String names (comma separated, e.g., E, A, D, G, B, E)"
                    onChange={handleTrackChange}
                    style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ddd' }}
                  />
                  <input
                    type="text"
                    name="frequencies"
                    value={trackForm.frequencies.join(', ')}
                    placeholder="Frequencies in Hz (comma separated, e.g., 82.41, 110.00, 146.83, 196.00, 246.94, 329.63)"
                    onChange={handleTrackChange}
                    style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ddd' }}
                  />
                </>
              )}
              <div style={{ background: 'white', padding: '1rem', borderRadius: '8px', border: '1px solid #e0e0e0' }}>
                <p style={{ margin: '0 0 0.5rem 0', color: '#666', fontSize: '0.9rem' }}>Strings: {trackForm.string_names.join(', ')}</p>
                <p style={{ margin: '0', color: '#666', fontSize: '0.9rem' }}>Frequencies: {trackForm.frequencies.map(f => (typeof f === 'number' ? f.toFixed(1) : f)).join(', ')} Hz</p>
              </div>
              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <button className="btn" onClick={saveTrack} disabled={loading} style={{ flex: 1 }}>
                  {editingTrackId ? 'Update Tuning' : 'Save Tuning'}
                </button>
                <button className="btn btn-danger" onClick={resetTrackForm} style={{ flex: 1 }}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="card">
        <h2 className="card-title">{view === 'all' ? '🌐 All Tunings' : view === 'my' ? '📝 My Tunings' : '⭐ Favorite Tunings'}</h2>

        {loading ? (
          <div style={{ textAlign: 'center' }}>
            <div className="spinner"></div>
          </div>
        ) : tracks.length === 0 ? (
          <p style={{ color: '#666', textAlign: 'center', padding: '2rem' }}>No tunings found.</p>
        ) : (
          <div className="grid grid-2">
            {tracks.map((track) => {
              const isFavorite = favoriteIds.has(track.id);
              const isOwner = view === 'my' || (token && username);
              return (
                <div key={track.id} className="card" style={{
                  padding: '1rem',
                  marginBottom: '1rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onClick={() => onOpenTrackPage && onOpenTrackPage(track.id)}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ flex: 1 }}>
                      <h3 style={{
                        margin: '0 0 0.25rem 0',
                        fontSize: '1.1rem',
                        color: '#333',
                        fontWeight: '600'
                      }}>
                        {track.title || 'Untitled'}
                      </h3>
                      <p style={{
                        margin: '0 0 0.25rem 0',
                        color: '#666',
                        fontSize: '0.95rem'
                      }}>
                        by <strong>{track.artist || 'Unknown Artist'}</strong>
                      </p>
                      <p style={{
                        margin: '0',
                        color: '#888',
                        fontSize: '0.85rem'
                      }}>
                        {getTuningDisplayName(track.tuning_name, apiTunings)}
                      </p>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                      {token && (
                        <button
                          className="btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleFavorite(track.id, isFavorite);
                          }}
                          style={{
                            padding: '0.4rem 0.8rem',
                            fontSize: '0.85rem'
                          }}
                        >
                          {isFavorite ? '⭐' : '☆'}
                        </button>
                      )}
                      {view === 'my' && (
                        <>
                          <button
                            className="btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              editTrack(track);
                            }}
                            style={{
                              padding: '0.4rem 0.8rem',
                              fontSize: '0.85rem'
                            }}
                          >
                            ✎
                          </button>
                          <button
                            className="btn btn-danger"
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteTrack(track.id);
                            }}
                            style={{
                              padding: '0.4rem 0.8rem',
                              fontSize: '0.85rem'
                            }}
                          >
                            🗑
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default UserTracks;

