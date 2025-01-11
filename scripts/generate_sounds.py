"""Generate placeholder sound files for development."""
import wave
import struct
import math
import os

def generate_sine_wave(frequency, duration, volume=0.5):
    """Generate a sine wave with given frequency and duration."""
    sample_rate = 44100
    num_samples = int(duration * sample_rate)
    samples = []
    
    for i in range(num_samples):
        sample = volume * math.sin(2 * math.pi * frequency * i / sample_rate)
        samples.append(struct.pack('h', int(sample * 32767)))
    
    return b''.join(samples)

def create_sound_file(filename, frequency, duration, volume=0.5):
    """Create a WAV file with given parameters."""
    with wave.open(filename, 'w') as wav_file:
        # Set parameters
        nchannels = 1
        sampwidth = 2
        framerate = 44100
        nframes = int(duration * framerate)
        comptype = 'NONE'
        compname = 'not compressed'
        
        # Set WAV file parameters
        wav_file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
        
        # Write audio data
        wav_file.writeframes(generate_sine_wave(frequency, duration, volume))

def main():
    """Create all placeholder sound files."""
    sounds_dir = os.path.join('assets', 'sounds')
    os.makedirs(sounds_dir, exist_ok=True)
    
    # Define sound parameters (frequency, duration, volume)
    sound_params = {
        'thrust': (220, 0.5, 0.3),      # Low rumble
        'shoot': (880, 0.1, 0.4),       # Short high pitch
        'explosion_large': (110, 0.8, 0.7),   # Long low boom
        'explosion_medium': (220, 0.5, 0.6),  # Medium boom
        'explosion_small': (440, 0.3, 0.5),   # Short higher boom
        'game_over': (220, 1.0, 0.6),   # Long low tone
        'level_complete': (660, 0.8, 0.5)  # Victory sound
    }
    
    # Create each sound file
    for name, (freq, duration, volume) in sound_params.items():
        filename = os.path.join(sounds_dir, f'{name}.wav')
        print(f"Generating {filename}...")
        create_sound_file(filename, freq, duration, volume)
        print(f"Created {filename}")

if __name__ == '__main__':
    main() 