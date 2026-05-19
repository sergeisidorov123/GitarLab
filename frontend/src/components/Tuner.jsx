import React from 'react';
import { useTuner } from '../hooks/useTuner';

const Tuner = () => {
  const { isListening, result, error, start, stop } = useTuner();

  return (
    <div className="card">
      <h2 className="card-title">🎸 Гитарный тюнер</h2>
      <p className="card-subtitle">
        Настройте струны вашей гитары с точностью
      </p>

      {error && (
        <div className="error-message">
          <strong>⚠️ Ошибка:</strong> {error}
        </div>
      )}

      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        {!isListening ? (
          <button onClick={start} className="btn">
            🎤 Старт 
          </button>
        ) : (
          <button onClick={stop} className="btn btn-danger">
            ⏹️ Остановить тюнинг
          </button>
        )}
      </div>

      {result && result.note && (
        <div style={{ textAlign: 'center' }}>
          <div style={{
            fontSize: '6rem',
            fontWeight: 'bold',
            color: result.is_in_tune ? '#4CAF50' : '#FF9800',
            marginBottom: '1rem',
            textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
          }}>
            {result.note}
          </div>

          <div style={{
            fontSize: '1.5rem',
            color: '#666',
            marginBottom: '2rem',
            fontWeight: '500'
          }}>
            {result.string ? `String: ${result.string}` : ''}
          </div>

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

          <div style={{
            fontSize: '1.2rem',
            marginBottom: '1rem',
            color: result.is_in_tune ? '#4CAF50' : '#FF9800',
            fontWeight: '600'
          }}>
            {result.suggestion === 'good' ? '🎯 Perfect!' :
             result.suggestion === 'up' ? '⬆️ Tune Up' :
             result.suggestion === 'down' ? '⬇️ Tune Down' :
             result.suggestion === 'a bit off' ? '🎵 Almost There' :
             result.suggestion === 'louder' ? '🔊 Play Louder' :
             result.suggestion}
          </div>

          <div style={{
            fontSize: '0.9rem',
            color: '#888',
            background: 'rgba(0, 0, 0, 0.05)',
            padding: '0.75rem',
            borderRadius: '8px',
            display: 'inline-block'
          }}>
            {result.frequency} Hz | {Math.abs(result.cents)} cents off
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
          <p>Play a note on your guitar...</p>
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
          <p>Click "Start Tuning" to begin tuning your guitar</p>
        </div>
      )}
    </div>
  );
};

export default Tuner;