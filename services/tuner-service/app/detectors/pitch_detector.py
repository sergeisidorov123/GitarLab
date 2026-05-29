import numpy as np
from collections import deque
from typing import Tuple


class PitchDetector:
    """
    Improved pitch detector for the tuner.

    - Robust bytes -> float conversion (handles float32, int16, int32 frames)
    - Normalization and short-history stability checks (median + cents checks)
    - Downsampling fallback for low-frequency / harmonic detections
    - Tunable minimum peak strength threshold
    """

    def __init__(
        self,
        sample_rate: int = 44100,
        min_freq: float = 80.0,
        max_freq: float = 1000.0,
        silence_threshold: float = 0.02,
        stability_frames: int = 3,
        max_freq_variation: float = 0.05,
        min_peak_strength: float = 0.12,
        min_peak_ratio: float = 1.4,
    ):
        self.sample_rate = sample_rate
        self.min_freq = min_freq
        self.max_freq = max_freq
        self.silence_threshold = silence_threshold
        self.stability_frames = stability_frames
        self.max_freq_variation = max_freq_variation
        self.min_peak_strength = min_peak_strength
        self.min_peak_ratio = min_peak_ratio

        self.freq_history = deque(maxlen=stability_frames)

    def _bytes_to_float_array(self, audio_bytes: bytes) -> np.ndarray:
        """Try to convert raw audio bytes into a float32 numpy array.

        Handles common encodings: float32, int16, int32.
        """
        if not audio_bytes:
            return np.array([], dtype=np.float32)

        # Try float32 first
        try:
            arr = np.frombuffer(audio_bytes, dtype=np.float32)
            if arr.size > 0 and np.isfinite(arr).all() and np.max(np.abs(arr)) <= 1e5:
                return arr
        except Exception:
            pass

        # Try int16
        try:
            arr16 = np.frombuffer(audio_bytes, dtype=np.int16)
            if arr16.size > 0:
                return (arr16.astype(np.float32) / 32768.0)
        except Exception:
            pass

        # Try int32
        try:
            arr32 = np.frombuffer(audio_bytes, dtype=np.int32)
            if arr32.size > 0:
                return (arr32.astype(np.float32) / 2147483648.0)
        except Exception:
            pass

        return np.array([], dtype=np.float32)

    def detect(self, audio_bytes: bytes) -> Tuple[float, bool]:
        """
        Determine main frequency from a chunk of audio bytes.

        Returns (frequency_hz, is_silence_or_invalid).
        """
        samples = self._bytes_to_float_array(audio_bytes)
        if samples.size < 256:
            return 0.0, True

        if not np.isfinite(samples).all():
            return 0.0, True

        # DC remove and normalize
        samples = samples - np.mean(samples)
        max_abs = np.max(np.abs(samples))
        if max_abs > 0:
            samples = samples / max_abs

        rms = np.sqrt(np.mean(samples**2))
        if rms < self.silence_threshold:
            return 0.0, True

        # Limit to a reasonable window to keep autocorrelation stable
        if len(samples) > 8192:
            samples = samples[-8192:]

        raw_freq, peak_strength, peak_ratio = self._autocorrelate_pitch(samples)

        # Also compute a direct YIN estimate here and prefer it when very confident
        try:
            yin_freq, yin_conf = self._yin_pitch(samples)
            if yin_freq > 0 and yin_conf >= 0.9 and yin_conf > (peak_strength - 0.02):
                raw_freq, peak_strength, peak_ratio = yin_freq, yin_conf, max(peak_ratio, 2.0)
        except Exception:
            pass

        # Fallback: try a downsampled pass to catch low fundamentals / harmonics
        if (raw_freq <= 0 or peak_strength < self.min_peak_strength or peak_ratio < self.min_peak_ratio) and len(samples) >= 512:
            ds = samples[::2]
            raw2, pk2, pr2 = self._autocorrelate_pitch(ds)
            if raw2 > 0 and pk2 >= self.min_peak_strength and pr2 >= self.min_peak_ratio:
                raw_freq, peak_strength, peak_ratio = raw2, pk2, pr2

        if raw_freq <= 0 or peak_strength < self.min_peak_strength or peak_ratio < self.min_peak_ratio:
            return 0.0, True

        if raw_freq < self.min_freq or raw_freq > self.max_freq * 2:
            # allow detection of harmonics up to twice max_freq but map to fundamental later
            return 0.0, True

        fundamental_freq = self._find_fundamental(raw_freq)
        self.freq_history.append(fundamental_freq)

        # Quick median-based stability check: accept if latest is close to median
        recent = list(self.freq_history)
        median_freq = float(np.median(recent))
        latest = float(recent[-1])
        if median_freq > 0:
            cents = abs(1200 * np.log2(latest / median_freq))
            if cents < 30:
                return median_freq, False

        if len(self.freq_history) < self.stability_frames:
            return 0.0, True

        avg_freq = float(np.mean(self.freq_history))
        std_freq = float(np.std(self.freq_history))
        variation = std_freq / avg_freq if avg_freq > 0 else 1.0

        if variation > self.max_freq_variation:
            return 0.0, True

        return avg_freq, False

    def _find_fundamental(self, detected_freq: float) -> float:
        """
        Map a detected frequency (possibly a harmonic) to the nearest guitar fundamental.
        Uses cents-based matching with two-pass thresholds to be robust to harmonics.
        """
        guitar_fundamentals = [82.41, 110.00, 146.83, 196.00, 246.94, 329.63]

        # If the detected frequency is already very close to an equal-tempered pitch,
        # treat it as the true pitch (avoid remapping harmonics like 440 -> 110).
        try:
            midi_note = 12 * np.log2(detected_freq / 440.0) + 69
            midi_rounded = int(round(midi_note))
            exact_freq = 440.0 * (2 ** ((midi_rounded - 69) / 12))
            cents_to_midi = abs(1200 * np.log2(detected_freq / exact_freq))
            if cents_to_midi < 40:
                return detected_freq
        except Exception:
            pass

        # First pass: tight cents threshold (≈40 cents)
        for fundamental in guitar_fundamentals:
            for mul in (1, 2, 3, 4):
                target = fundamental * mul
                if target <= 0:
                    continue
                cents = 1200 * np.log2(detected_freq / target)
                if abs(cents) < 40:
                    return fundamental

        # Second pass: looser threshold (≈80 cents)
        for fundamental in guitar_fundamentals:
            for mul in (1, 2, 3, 4):
                target = fundamental * mul
                if target <= 0:
                    continue
                cents = 1200 * np.log2(detected_freq / target)
                if abs(cents) < 80:
                    return fundamental

        # Fallback to detected frequency if no fundamental mapping found
        return detected_freq

    def _yin_pitch(self, samples: np.ndarray, threshold: float = 0.12) -> Tuple[float, float]:
        """
        Simple YIN implementation as a fallback pitch estimator.

        Returns (frequency_hz, confidence) where confidence is in [0,1].
        """
        x = samples.astype(np.float32)
        N = len(x)
        if N < 256:
            return 0.0, 0.0

        min_period = max(2, int(self.sample_rate / self.max_freq))
        max_period = int(self.sample_rate / self.min_freq)
        if max_period >= N:
            max_period = N - 1

        # Difference function
        d = np.zeros(max_period + 1, dtype=np.float64)
        for tau in range(1, max_period + 1):
            diff = x[:-tau] - x[tau:]
            d[tau] = np.sum(diff * diff)

        # Cumulative mean normalized difference
        cmnd = np.ones_like(d)
        running_sum = 0.0
        for tau in range(1, max_period + 1):
            running_sum += d[tau]
            if running_sum == 0:
                cmnd[tau] = 1.0
            else:
                cmnd[tau] = d[tau] * tau / running_sum

        # Search for threshold crossing
        tau_est = 0
        for tau in range(min_period, max_period + 1):
            if cmnd[tau] < threshold:
                # local minimum around tau
                while tau + 1 <= max_period and cmnd[tau + 1] < cmnd[tau]:
                    tau += 1
                tau_est = tau
                break

        if tau_est == 0:
            # fallback to global minimum in the interval
            tau_est = int(np.argmin(cmnd[min_period:max_period + 1]) + min_period)

        if tau_est <= 0:
            return 0.0, 0.0

        # Parabolic interpolation on cmnd for refined tau
        if tau_est <= 0 or tau_est >= len(cmnd) - 1:
            refined = float(tau_est)
        else:
            y_m1 = cmnd[tau_est - 1]
            y0 = cmnd[tau_est]
            y1 = cmnd[tau_est + 1]
            denom = (y_m1 - 2 * y0 + y1)
            if denom == 0:
                delta = 0.0
            else:
                delta = 0.5 * (y_m1 - y1) / denom
            refined = tau_est + delta

        frequency = self.sample_rate / refined if refined > 0 else 0.0
        confidence = max(0.0, 1.0 - float(cmnd[tau_est]))
        return frequency, confidence

    def _autocorrelate_pitch(self, samples: np.ndarray):
        """
        Improved autocorrelation: find local peaks, score by harmonic energy,
        perform parabolic interpolation and return
        (frequency_hz, peak_strength, peak_ratio).
        """
        samples = samples.astype(np.float32)
        samples = samples - np.mean(samples)

        if np.max(np.abs(samples)) < 1e-6:
            return 0.0, 0.0, 0.0

        window = np.hanning(len(samples))
        samples = samples * window

        correlation = np.correlate(samples, samples, mode='full')
        correlation = correlation[len(correlation)//2:]

        r0 = correlation[0] if len(correlation) > 0 else 0.0
        if r0 == 0:
            return 0.0, 0.0, 0.0

        corr = correlation / r0

        min_period = max(2, int(self.sample_rate / self.max_freq))
        max_period = int(self.sample_rate / self.min_freq)
        if max_period >= len(corr):
            max_period = len(corr) - 1

        if len(corr) <= min_period or max_period <= min_period:
            return 0.0, 0.0, 0.0

        search = corr[min_period:max_period]
        if len(search) == 0:
            return 0.0, 0.0, 0.0

        # Find local peaks in the search zone
        peaks = []
        for i in range(1, len(search) - 1):
            if search[i] > search[i - 1] and search[i] > search[i + 1]:
                peaks.append(i + min_period)

        # Fallback to global maximum if no local peaks
        if not peaks:
            peaks = [int(np.argmax(search) + min_period)]

        # Score peaks by harmonic consistency
        best_score = -1.0
        best_idx = None
        for p in peaks:
            score = corr[p]
            if p > 1 and p // 2 > 0:
                score += 0.5 * corr[p // 2]
            if p > 2 and p // 3 > 0:
                score += 0.33 * corr[p // 3]
            if p > 3 and p // 4 > 0:
                score += 0.25 * corr[p // 4]
            if score > best_score:
                best_score = score
                best_idx = p

        if best_idx is None:
            return 0.0, 0.0, 0.0

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

        frequency = self.sample_rate / refined if refined != 0 else 0.0
        peak_strength = float(corr[p])
        peak_ratio = peak_strength / (np.mean(np.abs(search)) + 1e-8)

        # If YIN is very confident, prefer it over a weak autocorrelation result
        try:
            yin_freq, yin_conf = self._yin_pitch(samples)
            if yin_freq > 0 and yin_conf > peak_strength and yin_conf > 0.7:
                return yin_freq, yin_conf, max(peak_ratio, 1.0)
        except Exception:
            pass

        return frequency, peak_strength, peak_ratio

    def reset_history(self):
        self.freq_history.clear()
