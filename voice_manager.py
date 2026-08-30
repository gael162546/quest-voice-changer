"""
Voice file management - Import and manage custom voice presets
"""

import os
import yaml
from pathlib import Path
from typing import List, Dict, Optional
import librosa
import soundfile as sf


class VoiceManager:
    """Handles importing and managing voice files as presets"""
    
    def __init__(self, voices_dir: str = "voices"):
        self.voices_dir = Path(voices_dir)
        self.voices_dir.mkdir(exist_ok=True)
        self.config_file = self.voices_dir / "voices.yaml"
        self.voices = self._load_voices_config()
        self.supported_formats = {'.wav', '.mp3', '.ogg', '.flac', '.m4a'}
    
    def _load_voices_config(self) -> Dict:
        """Load voice configuration from YAML"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _save_voices_config(self):
        """Save voice configuration to YAML"""
        with open(self.config_file, 'w') as f:
            yaml.dump(self.voices, f)
    
    def import_voice(self, file_path: str, voice_name: Optional[str] = None) -> bool:
        """
        Import a voice file to the voices directory
        
        Args:
            file_path: Path to the voice file
            voice_name: Custom name for the voice (defaults to filename)
            
        Returns:
            True if successful, False otherwise
        """
        file_path = Path(file_path)
        
        # Validate file
        if not file_path.exists():
            print(f"Error: File {file_path} not found")
            return False
        
        if file_path.suffix.lower() not in self.supported_formats:
            print(f"Error: Unsupported format {file_path.suffix}")
            return False
        
        # Set voice name
        if not voice_name:
            voice_name = file_path.stem
        
        try:
            # Load audio to validate
            audio, sr = librosa.load(str(file_path), sr=None)
            
            # Save to voices directory
            dest_path = self.voices_dir / f"{voice_name}.wav"
            sf.write(str(dest_path), audio, sr)
            
            # Update config
            self.voices[voice_name] = {
                'file': str(dest_path),
                'sample_rate': int(sr),
                'duration': float(len(audio) / sr),
                'original_file': file_path.name
            }
            self._save_voices_config()
            
            print(f"Successfully imported voice: {voice_name}")
            return True
            
        except Exception as e:
            print(f"Error importing voice: {e}")
            return False
    
    def get_voice(self, voice_name: str) -> Optional[Dict]:
        """Get voice metadata by name"""
        return self.voices.get(voice_name)
    
    def list_voices(self) -> List[str]:
        """List all available voices"""
        return list(self.voices.keys())
    
    def delete_voice(self, voice_name: str) -> bool:
        """Delete a voice preset"""
        if voice_name not in self.voices:
            print(f"Voice '{voice_name}' not found")
            return False
        
        try:
            file_path = Path(self.voices[voice_name]['file'])
            if file_path.exists():
                file_path.unlink()
            
            del self.voices[voice_name]
            self._save_voices_config()
            
            print(f"Deleted voice: {voice_name}")
            return True
            
        except Exception as e:
            print(f"Error deleting voice: {e}")
            return False
    
    def load_voice_audio(self, voice_name: str) -> Optional[tuple]:
        """
        Load audio data for a voice
        
        Returns:
            Tuple of (audio_array, sample_rate) or None if not found
        """
        voice = self.get_voice(voice_name)
        if not voice:
            print(f"Voice '{voice_name}' not found")
            return None
        
        try:
            audio, sr = librosa.load(voice['file'], sr=None)
            return audio, sr
        except Exception as e:
            print(f"Error loading voice audio: {e}")
            return None
