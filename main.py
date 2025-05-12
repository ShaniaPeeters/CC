import pyaudio
import numpy as np
import time
import board
from ledstrip import LEDStrip  # new import

#to run use  sudo $(which python) /home/piremote/Desktop/CC/main.py

# Parameters
CHUNK = 2048               # Number of audio samples per frame
FORMAT = pyaudio.paInt16   # Audio format (16-bit PCM)
CHANNELS = 1               # Number of audio channels (1 for mono)
RATE = 44100               # Sample rate (samples per second)

# LED strip configuration:
# Replace single LED strip configuration with multiple LED configurations:
# Each tuple is (pin, number of LEDs, brightness)
LED_CONFIGS = [
    (board.D18, 150, 1.0)  # First LED strip
]

# Create LEDStrip instances from LED_CONFIGS
ledstrips = [LEDStrip(pin, num, brightness) for (pin, num, brightness) in LED_CONFIGS]

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
            print(f"Volume: {volume}")

            # Determine how many LEDs to trigger.
            min_volume = 55
            max_volume = 100
            if volume < min_volume:
                trigger_count = 0
            else:
                # Linear scaling from 1 LED to full count across volume range.
                trigger_count = min(100, 1 + int((volume - min_volume) * (100 - 1) / (max_volume - min_volume)))
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