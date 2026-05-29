import numpy as np
from typing import Optional, Tuple

class NoteFinder:
    """Конвертирует частоту в ноту"""
    
    NOTES_4TH_OCTAVE = {
        'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
        'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
        'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
    }
    
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    @classmethod
    def frequency_to_note(cls, freq: float) -> Tuple[Optional[str], int]:
        """
        Преобразует частоту в ноту и отклонение в центах
        
        Returns:
            (note_name, cents_deviation)
        """
        if freq <= 0:
            return None, 0
        
        midi_note = 12 * np.log2(freq / 440) + 69
        midi_rounded = int(round(midi_note))

        # Allow a bit wider range to cover open / alternate tunings
        if midi_rounded < 28 or midi_rounded > 96:
            return None, 0

        exact_freq = 440 * (2 ** ((midi_rounded - 69) / 12))
        cents = int(round(1200 * np.log2(freq / exact_freq)))

        note_name = cls.NOTE_NAMES[midi_rounded % 12]
        octave = midi_rounded // 12 - 1

        return f"{note_name}{octave}", cents
    
    @classmethod
    def get_guitar_string(cls, freq: float) -> Optional[str]:
        """Определение струны гитары по частоте"""
        strings = {
            'E2 (6th)': 82.41,
            'A2 (5th)': 110.00,
            'D3 (4th)': 146.83,
            'G3 (3rd)': 196.00,
            'B3 (2nd)': 246.94,
            'E4 (1st)': 329.63
        }
        
        # Choose string by smallest cents difference (allowing octave mismatches)
        closest = None
        best_cents = float('inf')

        for name, str_freq in strings.items():
            # check several octave shifts to allow octave errors
            for shift in (-1, 0, 1):
                cand = str_freq * (2 ** shift)
                if cand <= 0:
                    continue
                cents = abs(1200 * np.log2(freq / cand)) if cand > 0 else float('inf')
                if cents < best_cents:
                    best_cents = cents
                    closest = name

        # require reasonably close (<= 150 cents ~ 1.5 semitones)
        return closest if best_cents <= 150 else None
    
    @classmethod
    def find_closest_string_and_cents(cls, freq: float) -> Tuple[Optional[str], float, int]:
        """
        Find the closest guitar string and calculate cents deviation from target.
        
        Returns:
            (string_name, target_frequency, cents_deviation)
        """
        strings = [
            ('E', 82.41),   
            ('A', 110.00),  
            ('D', 146.83),  
            ('G', 196.00),  
            ('B', 246.94),  
            ('E', 329.63)   
        ]
        
        closest_string = None
        closest_freq = 0.0
        best_score = float('inf')
        best_cents = 0

        for string_name, target_freq in strings:
            for harmonic in (1, 2, 3, 4):
                harmonic_freq = target_freq * harmonic
                if harmonic_freq <= 0:
                    continue

                cents_to_harmonic = abs(1200 * np.log2(freq / harmonic_freq))
                # penalize higher harmonics more strongly
                score = cents_to_harmonic + (harmonic - 1) * 50

                if score < best_score:
                    best_score = score
                    closest_string = string_name
                    closest_freq = target_freq
                    # cents relative to the fundamental (not harmonic)
                    best_cents = int(round(1200 * np.log2(freq / closest_freq)))

        # Accept only if score is not too large (loose threshold for robustness)
        if closest_string and best_score < 300:
            return closest_string, closest_freq, best_cents

        return None, 0.0, 0