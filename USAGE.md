# Usage Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/gael162546/quest-voice-changer.git
cd quest-voice-changer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Interactive Mode (Easiest)

```bash
python main.py
```

This opens an interactive menu where you can:
- List available voices
- List audio devices
- Import new voice files
- Load a voice preset
- Start processing

### Command Line Mode

```bash
# List available voices
python main.py --list-voices

# List audio devices
python main.py --list-devices

# Import a voice file
python main.py --import /path/to/voice.wav --voice-name "MyVoice"

# Load a voice and start processing
python main.py --load MyVoice --start --input-device 0 --output-device 0
```

## Importing Voice Files

### Supported Formats
- WAV
- MP3
- OGG
- FLAC
- M4A

### How to Import

1. **Interactive Mode:**
   ```
   > import /path/to/my_voice.wav
   ```
   Or with a custom name:
   ```
   > import /path/to/my_voice.wav MyCustomVoiceName
   ```

2. **Command Line:**
   ```bash
   python main.py --import /path/to/my_voice.wav --voice-name "MyVoice"
   ```

The voice file will be:
- Converted to WAV format
- Stored in the `voices/` directory
- Added to `voices/voices.yaml` configuration

### Finding Good Voice Samples

Good voice samples should be:
- **Clear audio** - No heavy background noise
- **3-30 seconds** - Long enough to capture characteristics, short for quick processing
- **Consistent volume** - Avoid clipping or very quiet sections
- **Isolated voice** - Minimal music or ambient sounds

### Creating Your Own Voice Samples

You can record voice samples using:
- `ffmpeg`: `ffmpeg -f pulse -i default.monitor output.wav`
- `audacity`: GUI audio editor
- `sound-recorder`: Simple built-in GNOME tool

## Processing Parameters

Edit `config.yaml` to adjust voice processing:

```yaml
processing:
  pitch_shift: 0        # -12 to 12 semitones
  speed_factor: 1.0     # 0.5 (half speed) to 2.0 (double speed)
  voice_strength: 0.5   # 0 (none) to 1.0 (full blend)
  normalize: true       # Auto-normalize loudness
```

### Parameter Explanations

- **pitch_shift**: Changes how high or low the voice is
  - Negative = Lower pitch
  - Positive = Higher pitch

- **speed_factor**: Changes playback speed
  - 0.5 = Half speed (slower, deeper)
  - 2.0 = Double speed (faster, higher)

- **voice_strength**: How much the imported voice characteristics affect your input
  - 0.0 = Just pitch/speed changes
  - 1.0 = Maximum voice blending

## Using with VRChat

1. **Set up virtual audio device** (optional, for VRChat to see the processed voice):
   ```bash
   # This requires additional PipeWire/PulseAudio configuration
   # Consult Linux audio documentation for your distro
   ```

2. **In VRChat settings**:
   - Select the appropriate audio input device
   - Your processed voice will be transmitted

3. **Test before going live**:
   - Run in interactive mode
   - Load a voice
   - Listen to output with headphones first

## Troubleshooting

### No audio input
- Check device list: `python main.py --list-devices`
- Ensure your microphone is enabled in system settings
- Try explicit device selection: `--input-device 1` (adjust index)

### Output is distorted
- Reduce `voice_strength` in config.yaml
- Lower pitch_shift values
- Check system volume levels

### Voice file import fails
- Ensure file format is supported (WAV, MP3, OGG, FLAC, M4A)
- Check file is not corrupted: `ffmpeg -v error -i file.wav -f null -`
- Try converting to WAV first: `ffmpeg -i input.mp3 output.wav`

### Performance issues
- Reduce chunk_size in config.yaml (more frequent but smaller chunks)
- Disable normalize if not needed
- Use shorter voice samples

## Advanced Usage

### Creating Voice Presets

You can manually edit `voices/voices.yaml` to create custom presets:

```yaml
CustomVoice:
  file: voices/custom.wav
  sample_rate: 48000
  duration: 5.5
  original_file: my_recording.wav
```

### Running as a Service

Create a systemd service file to run automatically:

```ini
[Unit]
Description=Quest Voice Changer
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/quest-voice-changer
ExecStart=/usr/bin/python3 main.py --load MyVoice --start
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then enable:
```bash
sudo systemctl enable quest-voice-changer
sudo systemctl start quest-voice-changer
```

## Tips & Tricks

1. **Layer voices**: Import multiple voices and switch between them
2. **Experiment with parameters**: Try different combinations of pitch/speed
3. **Clean audio**: Pre-process voice samples to remove noise (Audacity)
4. **Low latency**: Smaller chunk_size = lower latency but higher CPU usage
5. **Test with recording**: Record your processed voice to test before using in VRChat
