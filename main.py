#!/usr/bin/env python3
"""
Quest Voice Changer - Real-time voice processing for VRChat on Linux
"""

import sys
import argparse
import yaml
import time
from pathlib import Path
from typing import Optional

from voice_manager import VoiceManager
from voice_processor import VoiceProcessor
from audio_device import AudioDevice


class VoiceChanterApp:
    """Main application for voice changing"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.voice_manager = VoiceManager()
        self.voice_processor = VoiceProcessor(
            sample_rate=self.config['audio']['sample_rate']
        )
        self.audio_device = AudioDevice(
            sample_rate=self.config['audio']['sample_rate'],
            chunk_size=self.config['audio']['chunk_size']
        )
        self.current_voice = None
        self.is_running = False
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        if not Path(config_path).exists():
            print(f"Warning: Config file {config_path} not found, using defaults")
            return {
                'audio': {'sample_rate': 48000, 'chunk_size': 2048},
                'processing': {
                    'pitch_shift': 0,
                    'speed_factor': 1.0,
                    'voice_strength': 0.5,
                    'normalize': True
                }
            }
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def list_voices(self):
        """Display available voices"""
        voices = self.voice_manager.list_voices()
        if not voices:
            print("No voices imported yet. Use 'import <file>' to add voices.")
            return
        
        print("\nAvailable Voices:")
        print("-" * 50)
        for voice_name in voices:
            voice_info = self.voice_manager.get_voice(voice_name)
            duration = voice_info.get('duration', 0)
            sr = voice_info.get('sample_rate', 0)
            print(f"  • {voice_name}")
            print(f"    Duration: {duration:.2f}s | Sample Rate: {sr}Hz")
        print()
    
    def list_devices(self):
        """Display available audio devices"""
        print("\nInput Devices:")
        print("-" * 50)
        for device in self.audio_device.list_input_devices():
            print(f"  [{device['index']}] {device['name']}")
            print(f"      Channels: {device['channels']} | Sample Rate: {device['sample_rate']}Hz")
        
        print("\nOutput Devices:")
        print("-" * 50)
        for device in self.audio_device.list_output_devices():
            print(f"  [{device['index']}] {device['name']}")
            print(f"      Channels: {device['channels']} | Sample Rate: {device['sample_rate']}Hz")
        print()
    
    def import_voice(self, file_path: str, voice_name: Optional[str] = None):
        """Import a voice file"""
        if self.voice_manager.import_voice(file_path, voice_name):
            print(f"Voice imported successfully!")
        else:
            print(f"Failed to import voice from {file_path}")
    
    def load_voice(self, voice_name: str) -> bool:
        """Load a voice preset"""
        result = self.voice_manager.load_voice_audio(voice_name)
        if result:
            audio, sr = result
            self.voice_processor.set_voice_reference(audio, sr)
            self.current_voice = voice_name
            print(f"Loaded voice: {voice_name}")
            return True
        else:
            print(f"Failed to load voice: {voice_name}")
            return False
    
    def start_processing(self, input_device: Optional[int] = None, 
                        output_device: Optional[int] = None):
        """Start real-time voice processing"""
        if not self.current_voice:
            print("Error: No voice loaded. Use 'load <voice_name>' first.")
            return
        
        print(f"\nStarting voice processing with voice: {self.current_voice}")
        print("Press Ctrl+C to stop...\n")
        
        if not self.audio_device.open_input_stream(input_device):
            print("Failed to open input stream")
            return
        
        if not self.audio_device.open_output_stream(output_device):
            print("Failed to open output stream")
            self.audio_device.close()
            return
        
        self.is_running = True
        processing_config = self.config['processing']
        
        try:
            while self.is_running:
                # Read chunk
                chunk = self.audio_device.read_chunk()
                if chunk is None:
                    continue
                
                # Process chunk
                processed = self.voice_processor.process_chunk(
                    chunk,
                    pitch_shift=processing_config.get('pitch_shift', 0),
                    speed_factor=processing_config.get('speed_factor', 1.0),
                    voice_strength=processing_config.get('voice_strength', 0.5)
                )
                
                # Write chunk
                self.audio_device.write_chunk(processed)
        
        except KeyboardInterrupt:
            print("\n\nStopping voice processing...")
        finally:
            self.is_running = False
            self.audio_device.close()
    
    def interactive_menu(self):
        """Interactive menu for the application"""
        print("\n" + "=" * 50)
        print("Quest Voice Changer")
        print("=" * 50)
        
        while True:
            print("\nCommands:")
            print("  list-voices     - List available voices")
            print("  list-devices    - List audio devices")
            print("  import <file>   - Import a voice file")
            print("  load <voice>    - Load a voice preset")
            print("  start           - Start voice processing")
            print("  quit            - Exit application")
            print()
            
            cmd = input("Enter command: ").strip()
            
            if not cmd:
                continue
            
            parts = cmd.split()
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            if command == "list-voices":
                self.list_voices()
            
            elif command == "list-devices":
                self.list_devices()
            
            elif command == "import":
                if not args:
                    print("Usage: import <file_path> [voice_name]")
                    continue
                file_path = args[0]
                voice_name = args[1] if len(args) > 1 else None
                self.import_voice(file_path, voice_name)
            
            elif command == "load":
                if not args:
                    print("Usage: load <voice_name>")
                    continue
                self.load_voice(args[0])
            
            elif command == "start":
                self.start_processing()
            
            elif command == "quit":
                print("Goodbye!")
                break
            
            else:
                print(f"Unknown command: {command}")


def main():
    parser = argparse.ArgumentParser(
        description="Quest Voice Changer - Real-time voice processing for VRChat"
    )
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    parser.add_argument("--import", dest="import_file", help="Import a voice file")
    parser.add_argument("--voice-name", help="Name for imported voice")
    parser.add_argument("--load", help="Load a voice preset")
    parser.add_argument("--start", action="store_true", help="Start processing")
    parser.add_argument("--input-device", type=int, help="Input device index")
    parser.add_argument("--output-device", type=int, help="Output device index")
    parser.add_argument("--list-voices", action="store_true", help="List voices")
    parser.add_argument("--list-devices", action="store_true", help="List devices")
    
    args = parser.parse_args()
    
    app = VoiceChanterApp(args.config)
    
    if args.import_file:
        app.import_voice(args.import_file, args.voice_name)
    
    if args.list_voices:
        app.list_voices()
    
    if args.list_devices:
        app.list_devices()
    
    if args.load:
        app.load_voice(args.load)
    
    if args.start:
        app.start_processing(args.input_device, args.output_device)
    
    if not any([args.import_file, args.list_voices, args.list_devices, args.load, args.start]):
        app.interactive_menu()


if __name__ == "__main__":
    main()
