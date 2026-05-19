import React, { useEffect, useState } from 'react';
import { useTuner } from '../hooks/useTuner';

const API_URL = 'http://localhost:8002';

const TrackTuner = ({ trackId, token, onBack }) => {
  const [track, setTrack] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedStringIndex, setSelectedStringIndex] = useState(0);
  const { isListening, result, error: tunerError, start, stop } = useTuner();

  useEffect(() => {
    const loadTrack = async () => {
      try {
        const response = await fetch(`${API_URL}/tracks/${trackId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (!response.ok) {
          throw new Error('Failed to load track');
        }
        const data = await response.json();
        setTrack(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    if (trackId && token) {
      loadTrack();
    }
  }, [trackId, token]);

  if (loading) {
    return (
      <div className="card">
        <p>Загрузка трека...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="error-message">
          <strong>⚠️ Error:</strong> {error}
        </div>
        <button onClick={onBack} className="btn">
          ← Back to Library
        </button>
      </div>
    );
  }

  if (!track) {
    return (
      <div className="card">
        <p>Трек не найден</p>
        <button onClick={onBack} className="btn">
          ← Вернуться в библиотеку
        </button>
      </div>
    );
  }

  const targetFrequency = track.frequencies[selectedStringIndex];
  const targetNote = track.string_names[selectedStringIndex];

  return (
    <div className="card">
      <div style={{ marginBottom: '1.5rem' }}>
        <button onClick={onBack} className="btn btn-secondary" style={{ marginBottom: '1rem' }}>
          ← Back to Library
        </button>
        <h2 className="card-title">{track.title}</h2>
        <p style={{ color: '#666', marginBottom: '0.5rem' }}>{track.artist}</p>
        <p style={{ color: '#999', fontSize: '0.95rem' }}>
          Tuning: <strong>{track.tuning_name}</strong>
        </p>
      </div>

      {/* String Selector */}
      <div style={{ marginBottom: '2rem' }}>
        <p style={{ marginBottom: '0.75rem', fontWeight: '500', color: '#333' }}>
          Выберите струну для настройки:
        </p>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(60px, 1fr))',
          gap: '0.5rem',
          marginBottom: '1rem'
        }}>
          {track.string_names.map((note, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedStringIndex(idx)}
              style={{
                padding: '0.75rem',
                backgroundColor: selectedStringIndex === idx ? '#6366f1' : '#f3f4f6',
                color: selectedStringIndex === idx ? 'white' : '#333',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '1rem',
                transition: 'all 0.2s'
              }}
            >
              {note}
            </button>
          ))}
        </div>
        <div style={{
          padding: '1rem',
          backgroundColor: '#f9fafb',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <p style={{ color: '#666', marginBottom: '0.25rem' }}>Струна {selectedStringIndex + 1}:</p>
          <p style={{ fontSize: '1.8rem', fontWeight: 'bold', color: '#3b82f6' }}>
            {targetNote} - {targetFrequency.toFixed(2)} Гц
          </p>
        </div>
      </div>

      {tunerError && (
        <div className="error-message">
          <strong>⚠️ Ошибка тюнера:</strong> {tunerError}
        </div>
      )}

      {/* Tuner Controls */}
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        {!isListening ? (
          <button onClick={start} className="btn">
            🎤 Начать настройку струны {selectedStringIndex + 1}
          </button>
        ) : (
          <button onClick={stop} className="btn btn-danger">
            ⏹️ Остановить настройку
          </button>
        )}
      </div>

      {/* Tuner Result Display */}
      {result && result.note && (
        <div style={{ textAlign: 'center' }}>
          <div style={{
            fontSize: '5rem',
            fontWeight: 'bold',
            color: result.is_in_tune ? '#4CAF50' : '#FF9800',
            marginBottom: '1rem',
            textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
          }}>
            {result.note}
          </div>

          {/* Accuracy Meter */}
          <div style={{ margin: '2rem auto', maxWidth: '400px' }}>
            <div style={{
              width: '100%',
              height: '24px',
              backgroundColor: '#e0e0e0',
              borderRadius: '12px',
              overflow: 'hidden',
              position: 'relative'
            }}>
              <div style={{
                position: 'absolute',
                left: '50%',
                top: '0',
                bottom: '0',
                width: '2px',
                backgroundColor: '#333',
                zIndex: 2
              }} />
              <div style={{
                height: '100%',
                width: `${Math.min(50, Math.abs(result.cents) * 0.5)}%`,
                backgroundColor: result.is_in_tune ? '#4CAF50' : '#FF9800',
                position: 'absolute',
                left: result.cents < 0 ? `${50 - Math.min(50, Math.abs(result.cents) * 0.5)}%` : '50%',
                transition: 'all 0.1s ease'
              }} />
            </div>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginTop: '0.5rem',
              fontSize: '0.9rem',
              color: '#666'
            }}>
              <span>⬇️ Слишком низко</span>
              <span style={{
                color: result.is_in_tune ? '#4CAF50' : '#666',
                fontWeight: result.is_in_tune ? 'bold' : 'normal'
              }}>
                ✓ В тюне
              </span>
              <span>⬆️ Слишком высоко</span>
            </div>
          </div>

          {/* Status Message */}
          <div style={{
            fontSize: '1.2rem',
            marginBottom: '1rem',
            color: result.is_in_tune ? '#4CAF50' : '#FF9800',
            fontWeight: '600'
          }}>
            {result.is_in_tune ? '🎯 Идеально!' :
             result.suggestion === 'up' ? '⬆️ Подтянуть' :
             result.suggestion === 'down' ? '⬇️ Ослабить' :
             result.suggestion === 'a bit off' ? '🎵 Почти готово' :
             result.suggestion === 'louder' ? '🔊 Играй громче' :
             result.suggestion}
          </div>

          {/* Frequency Details */}
          <div style={{
            fontSize: '0.9rem',
            color: '#888',
            background: 'rgba(0, 0, 0, 0.05)',
            padding: '0.75rem',
            borderRadius: '8px',
            display: 'inline-block'
          }}>
            Обнаружено: {result.frequency} Гц | {Math.abs(result.cents)} центов отклонение
          </div>
        </div>
      )}

      {isListening && !result?.note && (
        <div style={{
          textAlign: 'center',
          color: '#666',
          fontSize: '1.2rem',
          marginTop: '2rem'
        }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎸</div>
          <p>Играй на струне <strong>{targetNote}</strong>...</p>
          <p style={{ fontSize: '0.9rem', color: '#888' }}>
            Убедитесь, что ваш микрофон включен и разрешен для этого сайта.
          </p>
        </div>
      )}

      {!isListening && !result && (
        <div style={{
          textAlign: 'center',
          color: '#666',
          fontSize: '1.1rem',
          marginTop: '2rem'
        }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem', opacity: 0.5 }}>🎸</div>
          <p>Нажмите "Начать настройку", чтобы настроить струну {selectedStringIndex + 1}</p>
        </div>
      )}
    </div>
  );
};

export default TrackTuner;
