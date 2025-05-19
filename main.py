import pyaudio
import numpy as np
import time
import board
from ledstrip import LEDStrip

# Parameters for audio processing
CHUNK = 2048               # Number of audio samples per frame
FORMAT = pyaudio.paInt16   # Audio format (16-bit PCM)
CHANNELS = 1               # Number of audio channels (mono)
RATE = 44100               # Sample rate

# Configurable volume thresholds
MIN_VOLUME = 40 
MAX_VOLUME = 100

# Configuration for physical LED strips and their segments.
# Each dictionary defines one physical strip along with its segments.
# Each segment is a tuple (start_index, number_of_leds)
PHYSICAL_LED_CONFIGS = [
    {
        'pin': board.D21,
        'total_leds': 150,
        'brightness': 1.0,
        'segments': [(0, 74), (148, 75)]
    },
    {
        'pin': board.D18,
        'total_leds': 150,
        'brightness': 1.0,
        'segments': [(0, 74), (148, 75)]
    },
    {
        'pin': board.D12,
        'total_leds': 150,
        'brightness': 1.0,
        'segments': [(0, 74), (148, 75)]
    }
]

# Create LEDStrip objects using the configuration above.
ledstrips = []
for config in PHYSICAL_LED_CONFIGS:
    pin = config['pin']
    total_leds = config['total_leds']
    brightness = config['brightness']
    for (start, num_leds) in config['segments']:
        ledstrips.append(LEDStrip(pin, total_leds, brightness, start=start, num_leds=num_leds))

def get_audio_input():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    # Initialize each LED segment
    for ls in ledstrips:
        ls.initialize()

    fade_delay = 3  # seconds

    print("Listening...")

    try:
        while True:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
            except OSError as e:
                print(f"Audio input overflowed: {e}")
                continue

            audio_data = np.frombuffer(data, dtype=np.int16)
            volume = np.sqrt(np.mean(audio_data**2))
            volume = np.nan_to_num(volume)
            if volume == 0:
                volume = MAX_VOLUME
            print(f"Volume: {volume}")

            if volume < MIN_VOLUME:
                trigger_count = 0
            else:
                trigger_count = min(100, 1 + int((volume - MIN_VOLUME) * (100 - 1) / (MAX_VOLUME - MIN_VOLUME)))
            print(f"Triggering {trigger_count} LEDs")

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

    for ls in ledstrips:
        ls.clear()

if __name__ == "__main__":
    get_audio_input()