import numpy as np
from typing import Tuple

class PitchDetector:
    """Детектит высоту звука методом автокорреляции"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
    
    def detect(self, audio_bytes: bytes) -> Tuple[float, bool]:
        """
        Определяет основную частоту аудиосигнала
        
        Returns:
            (frequency_hz, is_silence)
        """
        samples = np.frombuffer(audio_bytes, dtype=np.float32)
        
        if len(samples) < 100:
            return 0.0, True
        
        rms = np.sqrt(np.mean(samples**2))
        if rms < 0.01:
            return 0.0, True
        
        samples = samples - np.mean(samples)
        
        correlation = np.correlate(samples, samples, mode='full')
        correlation = correlation[len(correlation)//2:]
        
        min_period = int(self.sample_rate / 1000)  
        max_period = int(self.sample_rate / 80)    
        
        if len(correlation) <= min_period:
            return 0.0, False
        
        peak_index = np.argmax(correlation[min_period:max_period]) + min_period
        
        if peak_index < len(correlation) - 1:
            if correlation[peak_index] < correlation[peak_index - 1]:
                return 0.0, False
        
        frequency = self.sample_rate / peak_index
        
        if 80 <= frequency <= 1000:
            return frequency, False
        
        return 0.0, False