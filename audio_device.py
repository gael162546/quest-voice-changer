"""
Audio device handling for PipeWire/PulseAudio
"""

import pyaudio
from typing import List, Optional, Tuple
import numpy as np


class AudioDevice:
    """Handles audio input/output with PipeWire/PulseAudio"""
    
    def __init__(self, sample_rate: int = 48000, chunk_size: int = 2048):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
    
    def list_input_devices(self) -> List[dict]:
        """List available input devices"""
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxInputChannels'],
                    'sample_rate': int(info['defaultSampleRate'])
                })
        return devices
    
    def list_output_devices(self) -> List[dict]:
        """List available output devices"""
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxOutputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxOutputChannels'],
                    'sample_rate': int(info['defaultSampleRate'])
                })
        return devices
    
    def open_input_stream(self, device_index: Optional[int] = None) -> bool:
        """Open audio input stream"""
        try:
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=None
            )
            self.is_recording = True
            print(f"Input stream opened (sample rate: {self.sample_rate}Hz)")
            return True
        except Exception as e:
            print(f"Error opening input stream: {e}")
            return False
    
    def open_output_stream(self, device_index: Optional[int] = None) -> bool:
        """Open audio output stream"""
        try:
            self.output_stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                output=True,
                output_device_index=device_index,
                frames_per_buffer=self.chunk_size
            )
            print(f"Output stream opened")
            return True
        except Exception as e:
            print(f"Error opening output stream: {e}")
            return False
    
    def read_chunk(self) -> Optional[np.ndarray]:
        """Read audio chunk from input stream"""
        if not self.is_recording or self.stream is None:
            return None
        
        try:
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            return np.frombuffer(data, dtype=np.float32)
        except Exception as e:
            print(f"Error reading audio chunk: {e}")
            return None
    
    def write_chunk(self, audio: np.ndarray) -> bool:
        """Write audio chunk to output stream"""
        try:
            self.output_stream.write(audio.astype(np.float32).tobytes())
            return True
        except Exception as e:
            print(f"Error writing audio chunk: {e}")
            return False
    
    def close(self):
        """Close audio streams"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if hasattr(self, 'output_stream') and self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        self.is_recording = False
        print("Audio streams closed")
    
    def __del__(self):
        self.close()
        self.audio.terminate()
