import { useState, useRef, useCallback } from 'react';

export const useTuner = () => {
  const [isListening, setIsListening] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  const wsRef = useRef(null);
  const audioContextRef = useRef(null);
  const streamRef = useRef(null);
  
  const start = useCallback(async () => {
    setError(null);
    
    try {
      // Доступ к микрофону
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      // AudioContext
      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;
      
      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      
      source.connect(processor);
      processor.connect(audioContext.destination);
      
      // WebSocket
      const ws = new WebSocket('ws://localhost:8000/ws/tuner');
      wsRef.current = ws;
      
      ws.onopen = () => {
        setIsListening(true);
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setResult(data);
      };
      
      ws.onerror = () => {
        setError('WebSocket connection error');
        stop();
      };
      
      // Отправка аудио
      processor.onaudioprocess = (event) => {
        if (ws.readyState === WebSocket.OPEN) {
          const audioData = event.inputBuffer.getChannelData(0);
          ws.send(audioData.buffer);
        }
      };
      
      await audioContext.resume();
      
    } catch (err) {
      setError('Нет доступа к микрофону');
      console.error(err);
    }
  }, []);
  
  const stop = useCallback(() => {
    if (wsRef.current) wsRef.current.close();
    if (audioContextRef.current) audioContextRef.current.close();
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    setIsListening(false);
    setResult(null);
  }, []);
  
  return { isListening, result, error, start, stop };
};