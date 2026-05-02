import React from 'react';
import { useTuner } from '../hooks/useTuner';

const Tuner = () => {
  const { isListening, result, error, start, stop } = useTuner();
  
  return (
    <div style={{ textAlign: 'center', padding: '20px' }}>
      <h1>🎸 Guitar Tuner</h1>
      
      {error && (
        <div style={{ color: 'red', margin: '10px' }}>
          {error}
        </div>
      )}
      
      {!isListening ? (
        <button onClick={start} style={styles.button}>
          🎤 Start
        </button>
      ) : (
        <button onClick={stop} style={{...styles.button, backgroundColor: '#f44336'}}>
          ⏹️ Stop
        </button>
      )}
      
      {result && result.note && (
        <div style={{ marginTop: '30px' }}>
          <div style={{ fontSize: '80px', fontWeight: 'bold' }}>
            {result.note}
          </div>
          
          <div style={{ fontSize: '24px', color: '#666' }}>
            {result.string}
          </div>
          
          <div style={{ margin: '20px auto', width: '300px' }}>
            <div style={styles.meterBackground}>
              <div style={{
                ...styles.meterFill,
                width: `${Math.min(100, Math.abs(result.cents))}%`,
                transform: `translateX(${result.cents < 0 ? '0%' : '100%'})`,
                backgroundColor: result.is_in_tune ? '#4CAF50' : '#FF9800'
              }} />
            </div>
            
            <div style={styles.meterLabels}>
              <span>⬇️</span>
              <span>✓</span>
              <span>⬆️</span>
            </div>
          </div>
          
          <div style={{ fontSize: '18px', marginTop: '20px' }}>
            {result.suggestion}
          </div>
          
          <div style={{ fontSize: '14px', color: '#888', marginTop: '10px' }}>
            {result.frequency} Hz | {Math.abs(result.cents)} cents
          </div>
        </div>
      )}
      
      {isListening && !result?.note && (
        <div style={{ marginTop: '30px', color: '#666' }}>
          Играйте на гитаре...
        </div>
      )}
    </div>
  );
};

const styles = {
  button: {
    padding: '15px 30px',
    fontSize: '18px',
    backgroundColor: '#4CAF50',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    marginTop: '20px'
  },
  meterBackground: {
    width: '100%',
    height: '20px',
    backgroundColor: '#ddd',
    borderRadius: '10px',
    overflow: 'hidden'
  },
  meterFill: {
    height: '100%',
    transition: 'transform 0.05s linear'
  },
  meterLabels: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: '5px',
    fontSize: '14px'
  }
};

export default Tuner;