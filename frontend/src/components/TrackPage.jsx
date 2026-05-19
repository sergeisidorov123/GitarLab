import React, { useEffect, useState } from 'react';
import { useTuner } from '../hooks/useTuner';
import Comments from './Comments';

const API_URL = 'http://localhost:8002';

const TrackPage = ({ trackId, token, onBack }) => {
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
          throw new Error(`Failed to load track: ${response.status}`);
        }
        const data = await response.json();
        setTrack(data);
        setLoading(false);
      } catch (err) {
        console.error('Error loading track:', err);
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
          <strong>⚠️ Ошибка:</strong> {error}
        </div>
        <button onClick={onBack} className="btn">
          ← Возврат к библиотеке
        </button>
      </div>
    );
  }

  if (!track) {
    return (
      <div className="card">
        <p>Трек не найден</p>
        <button onClick={onBack} className="btn">
          ← Возврат к библиотеке
        </button>
      </div>
    );
  }

  const targetFrequency = track.frequencies[selectedStringIndex];
  const targetNote = track.string_names[selectedStringIndex];

  return (
    <div>
      {/* Track Header */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
          <div>
            <h1 className="card-title" style={{ margin: '0 0 0.5rem 0' }}>{track.title}</h1>
            <p style={{ color: '#666', margin: '0 0 0.5rem 0', fontSize: '1.2rem' }}>
              от <strong>{track.artist}</strong>
            </p>
            <p style={{ color: '#999', margin: '0 0 0.5rem 0', fontSize: '1rem' }}>
              Тюнинг: <strong>{track.tuning_name}</strong>
            </p>
            {track.genres && track.genres.length > 0 && (
              <p style={{ color: '#777', margin: '0', fontSize: '0.95rem' }}>
                Жанры: {track.genres.map((genre) => genre.name).join(', ')}
              </p>
            )}
          </div>
          <button onClick={onBack} className="btn btn-secondary">
            ← Возврат к библиотеке
          </button>
        </div>

        {/* Tuning Display */}
        <div style={{ background: '#f9fafb', padding: '1.5rem', borderRadius: '12px', marginBottom: '2rem' }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#333' }}>🎸 Детали тюнинга</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(80px, 1fr))', gap: '1rem' }}>
            {track.string_names.map((note, idx) => (
              <div
                key={idx}
                style={{
                  textAlign: 'center',
                  padding: '1rem',
                  backgroundColor: selectedStringIndex === idx ? '#3b82f6' : '#ffffff',
                  color: selectedStringIndex === idx ? 'white' : '#333',
                  borderRadius: '8px',
                  border: '2px solid #e5e7eb',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  fontWeight: '600'
                }}
                onClick={() => setSelectedStringIndex(idx)}
              >
                <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>{note}</div>
                <div style={{ fontSize: '0.8rem', opacity: 0.8 }}>
                  {track.frequencies[idx].toFixed(1)} Hz
                </div>
                <div style={{ fontSize: '0.7rem', opacity: 0.6, marginTop: '0.25rem' }}>
                  Струна {idx + 1}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Tuner Section */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <h2 className="card-title">🎵 Гитарный тюнер</h2>
        <p className="card-subtitle">
          Настройте свою гитару в соответствии с тюнингом этого трека
        </p>

        {tunerError && (
          <div className="error-message">
            <strong>⚠️ Ошибка тюнера:</strong> {tunerError}
          </div>
        )}

        {/* Current String Display */}
        <div style={{
          textAlign: 'center',
          marginBottom: '2rem',
          padding: '1.5rem',
          backgroundColor: '#f9fafb',
          borderRadius: '12px'
        }}>
          <p style={{ color: '#666', marginBottom: '0.5rem' }}>Сейчас настраивается:</p>
          <p style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#3b82f6', margin: '0' }}>
            {targetNote}
          </p>
          <p style={{ color: '#888', margin: '0.25rem 0 0 0' }}>
            {targetFrequency.toFixed(2)} Гц • Струна {selectedStringIndex + 1}
          </p>
        </div>

        {/* Tuner Controls */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          {!isListening ? (
            <button onClick={start} className="btn">
              🎤 Начать настройку {targetNote}
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
              fontSize: '4rem',
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
            <p>Нажмите "Начать настройку", чтобы настроить струну {targetNote}</p>
          </div>
        )}
      </div>

      {/* Comments Section */}
      <div className="card">
        <Comments trackId={trackId} token={token} />
      </div>
    </div>
  );
};

export default TrackPage;