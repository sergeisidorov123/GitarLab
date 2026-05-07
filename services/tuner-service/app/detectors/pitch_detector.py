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
        silence_threshold: float = 0.008, 
        stability_frames: int = 3,        
        max_freq_variation: float = 0.08  
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
        if len(samples) < 256:
            return 0.0, True

        if not np.isfinite(samples).all():
            return 0.0, True

        rms = np.sqrt(np.mean(samples**2))
        if rms < self.silence_threshold:
            return 0.0, True

        raw = self._autocorrelate_pitch(samples)
        if isinstance(raw, tuple):
            raw_freq, peak_strength = raw
        else:
            raw_freq = float(raw)
            peak_strength = 0.0

        if raw_freq <= 0 or peak_strength < 0.18:
            self.freq_history.clear()
            return 0.0, True

        if raw_freq < self.min_freq or raw_freq > self.max_freq:
            self.freq_history.clear()
            return 0.0, True

        fundamental_freq = self._find_fundamental(raw_freq)
        self.freq_history.append(fundamental_freq)

        if len(self.freq_history) < 2:
            return 0.0, True

        recent_readings = list(self.freq_history)[-min(3, len(self.freq_history)):]
        recent_avg = np.mean(recent_readings)
        recent_std = np.std(recent_readings)
        recent_variation = recent_std / recent_avg if recent_avg > 0 else 1.0

        if recent_variation < 0.03:
            return recent_avg, False

        if len(self.freq_history) < self.stability_frames:
            return 0.0, True

        avg_freq = np.mean(self.freq_history)
        std_freq = np.std(self.freq_history)
        variation = std_freq / avg_freq if avg_freq > 0 else 1.0

        if variation > self.max_freq_variation:
            return 0.0, True

        return avg_freq, False
    
    def _find_fundamental(self, detected_freq: float) -> float:
        guitar_fundamentals = [82.41, 110.00, 146.83, 196.00, 246.94, 329.63]
        
        if detected_freq <= 0:
            return detected_freq

        # Exact or very close fundamental
        for fundamental in guitar_fundamentals:
            if abs(detected_freq - fundamental) < 3:
                return fundamental

        # If we detected a strong harmonic, map it back to the correct string fundamental.
        for fundamental in guitar_fundamentals:
            for multiple in (2, 3, 4):
                expected = fundamental * multiple
                if expected <= 0:
                    continue
                if abs(detected_freq / expected - 1.0) < 0.03:
                    return fundamental

        # If there is a near-miss on the fundamental, prefer the string note.
        for fundamental in guitar_fundamentals:
            if abs(detected_freq - fundamental) < 8:
                return fundamental

        return detected_freq
    
    def _autocorrelate_pitch(self, samples: np.ndarray):
        """
        Improved autocorrelation: find local peaks, score by harmonic energy,
        perform parabolic interpolation and return (frequency_hz, peak_strength).
        """
        samples = samples.astype(np.float32)
        samples = samples - np.mean(samples)

        if np.max(np.abs(samples)) < 1e-6:
            return 0.0, 0.0

        window = np.hanning(len(samples))
        samples = samples * window

        correlation = np.correlate(samples, samples, mode='full')
        correlation = correlation[len(correlation)//2:]

        r0 = correlation[0] if len(correlation) > 0 else 0.0
        if r0 == 0:
            return 0.0, 0.0

        corr = correlation / r0

        min_period = int(self.sample_rate / self.max_freq)
        max_period = int(self.sample_rate / self.min_freq)
        if max_period >= len(corr):
            max_period = len(corr) - 1

        if len(corr) <= min_period or max_period <= min_period:
            return 0.0, 0.0

        search = corr[min_period:max_period]
        if len(search) == 0:
            return 0.0, 0.0

        # Find local peaks in the search zone
        peaks = []
        for i in range(1, len(search) - 1):
            if search[i] > search[i - 1] and search[i] > search[i + 1]:
                peaks.append(i + min_period)

        # Fallback to global maximum if no local peaks
        if not peaks:
            peaks = [int(np.argmax(search) + min_period)]

        # Score peaks by harmonic consistency (fundamental should have harmonic energy)
        best_score = -1.0
        best_idx = None
        for p in peaks:
            score = corr[p]
            if 2 * p < len(corr):
                score += 0.5 * corr[2 * p]
            if 3 * p < len(corr):
                score += 0.33 * corr[3 * p]
            if 4 * p < len(corr):
                score += 0.25 * corr[4 * p]
            if score > best_score:
                best_score = score
                best_idx = p

        if best_idx is None:
            return 0.0, 0.0

        p = int(best_idx)

        # Parabolic interpolation for sub-sample peak estimation
        if p <= 0 or p >= len(corr) - 1:
            refined = float(p)
        else:
            y_m1 = corr[p - 1]
            y0 = corr[p]
            y1 = corr[p + 1]
            denom = (y_m1 - 2 * y0 + y1)
            if denom == 0:
                delta = 0.0
            else:
                delta = 0.5 * (y_m1 - y1) / denom
            refined = p + delta

        # As a final safeguard, compute scores for known guitar string fundamentals
        # and prefer a string-based candidate if it has stronger harmonic support.
        guitar_fundamentals = [82.41, 110.00, 146.83, 196.00, 246.94, 329.63]
        best_string_score = -1.0
        best_string_period = None
        best_string_freq = None
        for f0 in guitar_fundamentals:
            period = int(round(self.sample_rate / f0))
            if period <= 0 or period >= len(corr):
                continue
            s = corr[period]
            if period // 2 > 0:
                s += 0.5 * corr[period // 2]
            if period // 3 > 0:
                s += 0.33 * corr[period // 3]
            if s > best_string_score:
                best_string_score = s
                best_string_period = period
                best_string_freq = f0

        # If a canonical guitar string shows stronger harmonic support, prefer it
        if best_string_score > 0 and best_string_score > best_score * 1.15:
            # refine around the string period
            p_str = best_string_period
            if p_str <= 0 or p_str >= len(corr) - 1:
                refined = float(p_str)
            else:
                y_m1 = corr[p_str - 1]
                y0 = corr[p_str]
                y1 = corr[p_str + 1]
                denom = (y_m1 - 2 * y0 + y1)
                if denom == 0:
                    delta = 0.0
                else:
                    delta = 0.5 * (y_m1 - y1) / denom
                refined = p_str + delta
            frequency = self.sample_rate / refined
            peak_strength = float(corr[int(round(p_str))])
            return frequency, peak_strength

        # Otherwise use best peak
        if refined == 0:
            return 0.0, 0.0

        frequency = self.sample_rate / refined
        peak_strength = float(corr[p])
        return frequency, peak_strength
    
    def reset_history(self):
        self.freq_history.clear()