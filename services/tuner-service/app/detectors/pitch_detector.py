import numpy as np
from collections import deque
from typing import Tuple

class PitchDetector:
    """
    Детектор высоты звука для гитары с фильтрацией ложных срабатываний.
    Использует автокорреляцию + проверку стабильности частоты во времени.
    """
    
    def __init__(
        self,
        sample_rate: int = 44100,
        min_freq: float = 80.0,          
        max_freq: float = 1000.0,        
        silence_threshold: float = 0.01,  
        stability_frames: int = 5,        
        max_freq_variation: float = 0.05  
    ):
        self.sample_rate = sample_rate
        self.min_freq = min_freq
        self.max_freq = max_freq
        self.silence_threshold = silence_threshold
        self.stability_frames = stability_frames
        self.max_freq_variation = max_freq_variation
        
        self.freq_history = deque(maxlen=stability_frames)
    
    def detect(self, audio_bytes: bytes) -> Tuple[float, bool]:
        """
        Определяет основную частоту аудиосигнала.
        
        Returns:
            (frequency_hz, is_silence_or_invalid)
            - если частота стабильна и в диапазоне гитары -> (freq, False)
            - иначе -> (0.0, True)
        """
        samples = np.frombuffer(audio_bytes, dtype=np.float32)
        if len(samples) < 100:
            return 0.0, True
        
        rms = np.sqrt(np.mean(samples**2))
        if rms < self.silence_threshold:
            return 0.0, True
        
        raw_freq = self._autocorrelate_pitch(samples)
        
        if raw_freq < self.min_freq or raw_freq > self.max_freq:
            return 0.0, True
        
        self.freq_history.append(raw_freq)
        if len(self.freq_history) < self.stability_frames:
            return 0.0, True
        
        avg_freq = np.mean(self.freq_history)
        std_freq = np.std(self.freq_history)
        variation = std_freq / avg_freq if avg_freq > 0 else 1.0
        
        if variation > self.max_freq_variation:
            return 0.0, True
        
        return avg_freq, False
    
    def _autocorrelate_pitch(self, samples: np.ndarray) -> float:
        """
        Алгоритм автокорреляции для нахождения основной частоты.
        Возвращает частоту в герцах или 0.0, если не удалось.
        """
        samples = samples - np.mean(samples)
        
        correlation = np.correlate(samples, samples, mode='full')
        correlation = correlation[len(correlation)//2:]
        
        min_period = int(self.sample_rate / self.max_freq)   
        max_period = int(self.sample_rate / self.min_freq)   
        
        if len(correlation) <= min_period:
            return 0.0
        
        search_zone = correlation[min_period:max_period]
        if len(search_zone) == 0:
            return 0.0
            
        peak_index = np.argmax(search_zone) + min_period
        
        if peak_index < len(correlation) - 1:
            if correlation[peak_index] < correlation[peak_index - 1]:
                return 0.0
        
        frequency = self.sample_rate / peak_index
        return frequency
    
    def reset_history(self):
        self.freq_history.clear()