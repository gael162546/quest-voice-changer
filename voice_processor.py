"""
Core voice processing engine
"""

import numpy as np
import librosa
import soundfile as sf
from typing import Optional, Tuple
import pyrubberband as pyrb


class VoiceProcessor:
    """Processes audio using imported voice presets"""
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.reference_audio = None
        self.reference_sr = None
    
    def set_voice_reference(self, audio: np.ndarray, sr: int):
        """Set the reference voice audio to process towards"""
        # Resample to target sample rate
        if sr != self.sample_rate:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sample_rate)
        
        self.reference_audio = audio
        self.reference_sr = self.sample_rate
    
    def pitch_shift(self, audio: np.ndarray, semitones: float) -> np.ndarray:
        """
        Shift pitch by semitones
        
        Args:
            audio: Input audio array
            semitones: Number of semitones to shift (can be negative)
            
        Returns:
            Pitch-shifted audio
        """
        try:
            shifted = pyrb.pitch_shift(audio, self.sample_rate, semitones)
            return shifted
        except Exception as e:
            print(f"Error in pitch shift: {e}")
            return audio
    
    def time_stretch(self, audio: np.ndarray, rate: float) -> np.ndarray:
        """
        Stretch audio in time (speed up/slow down)
        
        Args:
            audio: Input audio array
            rate: Speed multiplier (0.5 = half speed, 2.0 = double speed)
            
        Returns:
            Time-stretched audio
        """
        try:
            stretched = pyrb.time_stretch(audio, self.sample_rate, rate)
            return stretched
        except Exception as e:
            print(f"Error in time stretch: {e}")
            return audio
    
    def apply_voice_characteristics(self, input_audio: np.ndarray, 
                                    voice_strength: float = 0.5) -> np.ndarray:
        """
        Apply characteristics from reference voice to input audio
        
        Args:
            input_audio: Input microphone audio
            voice_strength: How much to blend voice characteristics (0-1)
            
        Returns:
            Processed audio with voice characteristics
        """
        if self.reference_audio is None:
            return input_audio
        
        # Ensure same length for processing
        min_len = min(len(input_audio), len(self.reference_audio))
        input_audio = input_audio[:min_len]
        ref_audio = self.reference_audio[:min_len]
        
        # Extract spectral characteristics from reference
        input_spec = librosa.stft(input_audio)
        ref_spec = librosa.stft(ref_audio)
        
        # Get magnitude and phase
        input_mag, input_phase = np.abs(input_spec), np.angle(input_spec)
        ref_mag = np.abs(ref_spec)
        
        # Blend magnitudes (voice characteristics)
        blended_mag = (1 - voice_strength) * input_mag + voice_strength * ref_mag
        
        # Reconstruct with blended magnitude and input phase
        blended_spec = blended_mag * np.exp(1j * input_phase)
        output = librosa.istft(blended_spec)
        
        return output
    
    def normalize(self, audio: np.ndarray, target_db: float = -20) -> np.ndarray:
        """
        Normalize audio to target loudness
        
        Args:
            audio: Input audio
            target_db: Target loudness in dB
            
        Returns:
            Normalized audio
        """
        # Calculate current loudness
        S = librosa.stft(audio)
        S_db = librosa.power_to_db(np.abs(S) ** 2)
        loudness = np.mean(S_db)
        
        # Calculate gain
        gain_db = target_db - loudness
        gain = 10 ** (gain_db / 20)
        
        return np.clip(audio * gain, -1.0, 1.0)
    
    def process_chunk(self, chunk: np.ndarray, 
                     pitch_shift: float = 0,
                     speed_factor: float = 1.0,
                     voice_strength: float = 0.5) -> np.ndarray:
        """
        Process a single audio chunk with all effects
        
        Args:
            chunk: Audio chunk to process
            pitch_shift: Semitones to shift pitch
            speed_factor: Speed multiplier
            voice_strength: Voice characteristic blend (0-1)
            
        Returns:
            Processed audio chunk
        """
        output = chunk.copy()
        
        if pitch_shift != 0:
            output = self.pitch_shift(output, pitch_shift)
        
        if speed_factor != 1.0:
            output = self.time_stretch(output, speed_factor)
        
        if self.reference_audio is not None and voice_strength > 0:
            output = self.apply_voice_characteristics(output, voice_strength)
        
        output = self.normalize(output)
        
        return output
