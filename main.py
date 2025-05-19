import pyaudio
import numpy as np
import time
import board
from ledstrip import LEDStrip  # new import
dir(board)
#to run use  sudo $(which python) /home/piremote/Desktop/CC/main.py

# Parameters
CHUNK = 2048               # Number of audio samples per frame
FORMAT = pyaudio.paInt16   # Audio format (16-bit PCM)
CHANNELS = 1               # Number of audio channels (1 for mono)
RATE = 44100               # Sample rate (samples per second)

# Configurable volume thresholds
MIN_VOLUME = 40 
MAX_VOLUME = 100

# LED strip configuration:
# Replace single LED strip configuration with multiple LED configurations:
# Each tuple is (pin, number of LEDs, brightness)
LED_CONFIGS = [
    (board.D12, 0, 148, 1.0, False),  # First LED strip
    (board.D18, 0, 148, 1.0, False), # Second LED strip
    (board.D21, 0,148, 1.0, False)  # Third LED strip
]

# Create LEDStrip instances from LED_CONFIGS

ledstrips = [LEDStrip(pin, start, num, brightness, reverse) for (pin, start, num, brightness, reverse) in LED_CONFIGS]

def get_audio_input():
    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open audio stream
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    # Initialize LED strips
    for ls in ledstrips:
        ls.initialize()

    fade_delay = 3  # seconds

    print("Listening...")

    try:
        while True:
            # Read audio input
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
            except OSError as e:
                print(f"Audio input overflowed: {e}")
                continue

            # Process audio data to calculate volume (RMS)
            audio_data = np.frombuffer(data, dtype=np.int16)
            volume = np.sqrt(np.mean(audio_data**2))
            volume = np.nan_to_num(volume)
            if volume == 0:
                volume = MAX_VOLUME  # act as if it's max audio level
            print(f"Volume: {volume}")

            # Determine how many LEDs to trigger.
            if volume < MIN_VOLUME:
                trigger_count = 0
            else:
                # Linear scaling from 1 LED to full count across volume range.
                trigger_count = min(100, 1 + int((volume - MIN_VOLUME) * (100 - 1) / (MAX_VOLUME - MIN_VOLUME)))
            print(f"Triggering {trigger_count} LEDs")

            # Update each LED strip: trigger LEDs and fade
            for ls in ledstrips:
                transitions = ls.update_leds(trigger_count)
                ls.propagate(trigger_count, transitions)
                ls.fade(fade_delay)
                ls.show()

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Stopping...")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Clear all LED strips
    for ls in ledstrips:
        ls.clear()

if __name__ == "__main__":
    get_audio_input()