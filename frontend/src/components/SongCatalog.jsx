import React, { useState, useEffect } from 'react';

const SongCatalog = () => {
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSong, setSelectedSong] = useState(null);

  useEffect(() => {
    fetchSongs();
  }, []);

  const fetchSongs = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8001/songs/');
      if (!response.ok) {
        throw new Error('Failed to fetch songs');
      }
      const data = await response.json();
      setSongs(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchSongDetails = async (songId) => {
    try {
      const response = await fetch(`http://localhost:8001/songs/${songId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch song details');
      }
      const data = await response.json();
      setSelectedSong(data);
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) {
    return (
      <div className="card">
        <div className="spinner"></div>
        <p style={{ textAlign: 'center', color: '#666' }}>Загрузка песен...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
        <button className="btn" onClick={fetchSongs}>
          Попробовать снова
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="card">
        <h2 className="card-title">🎼 Каталог песен</h2>
        <p className="card-subtitle">
          Просмотр песен и их тюнингов
        </p>

        {songs.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>
            Песни не найдены. Сервис каталога может быть не запущен.
          </p>
        ) : (
          <div className="grid grid-3">
            {songs.map((song) => (
              <div
                key={song.id}
                className="card"
                style={{
                  cursor: 'pointer',
                  transition: 'transform 0.2s ease',
                  padding: '1.5rem'
                }}
                onClick={() => fetchSongDetails(song.id)}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-5px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <h3 style={{ margin: '0 0 0.5rem 0', color: '#333' }}>
                  {song.title}
                </h3>
                <p style={{ margin: '0', color: '#666', fontSize: '0.9rem' }}>
                  by {song.artist}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedSong && (
        <div className="card">
          <h2 className="card-title">🎵 Детали песни</h2>

          <div style={{ marginBottom: '2rem' }}>
            <h3 style={{ color: '#333', margin: '0 0 0.5rem 0' }}>
              {selectedSong.title}
            </h3>
            <p style={{ color: '#666', margin: '0 0 1rem 0', fontSize: '1.1rem' }}>
              by {selectedSong.artist}
            </p>
          </div>

          <div>
            <h4 style={{ color: '#333', margin: '0 0 1rem 0' }}>
              🎸 Тюнинг: {selectedSong.tuning.name}
            </h4>

            <div className="grid grid-2">
              <div>
                <h5 style={{ color: '#555', margin: '0 0 0.5rem 0' }}>
                  Названия струн
                </h5>
                <ul style={{ paddingLeft: '1.5rem' }}>
                  {selectedSong.tuning.string_names.map((name, index) => (
                    <li key={index} style={{ color: '#666', marginBottom: '0.25rem' }}>
                      {name}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h5 style={{ color: '#555', margin: '0 0 0.5rem 0' }}>
                  Частоты (Гц)
                </h5>
                <ul style={{ paddingLeft: '1.5rem' }}>
                  {selectedSong.tuning.frequencies.map((freq, index) => (
                    <li key={index} style={{ color: '#666', marginBottom: '0.25rem' }}>
                      {freq.toFixed(1)} Hz
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          <button
            className="btn"
            onClick={() => setSelectedSong(null)}
            style={{ marginTop: '2rem' }}
          >
            Закрыть детали
          </button>
        </div>
      )}
    </div>
  );
};

export default SongCatalog;