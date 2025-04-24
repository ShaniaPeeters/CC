import pyaudio
import numpy as np
import time
import board  # Required for neopixel
import neopixel  # Correct import for the neopixel library

# to run use this: sudo $(which python) /home/piremote/Desktop/CC/main.py

# Parameters
CHUNK = 2048               # Number of audio samples per frame
FORMAT = pyaudio.paInt16   # Audio format (16-bit PCM)
CHANNELS = 1               # Number of audio channels (1 for mono)
RATE = 44100               # Sample rate (samples per second)

# LED strip configuration:
LED_COUNT = 30           # Number of LED pixels.
LED_PIN = board.D18      # GPIO pin connected to the pixels (D18 for PWM).
LED_BRIGHTNESS = 1.0     # Brightness (0.0 to 1.0)

# Color definitions
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
RED    = (255, 0, 0)
OFF    = (0, 0, 0)

def get_audio_input():
    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open stream
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    # Initialize LED strip
    strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

    print("Listening...")

    try:
        while True:
            # Fade each LED by reducing brightness
            for i in range(LED_COUNT):
                current = strip[i]
                faded = tuple(max(0, int(c * 0.9)) for c in current)
                strip[i] = faded

            # Read audio input
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
            except OSError as e:
                print(f"Audio input overflowed: {e}")
                continue

            # Convert data to numpy array and calculate volume (RMS)
            audio_data = np.frombuffer(data, dtype=np.int16)
            volume = np.sqrt(np.mean(audio_data**2))
            print(f"Volume: {volume}")

            # Determine how many LEDs to trigger.
            # Adjust the divisor (here 4000) to control sensitivity.
            trigger_count = min(LED_COUNT, int((volume / 4000) * LED_COUNT))
            print(f"Triggering {trigger_count} LEDs")

            # For the triggered LEDs, update color based on current state.
            for i in range(trigger_count):
                current = strip[i]
                if current == OFF:
                    strip[i] = YELLOW
                elif current == YELLOW:
                    strip[i] = ORANGE
                elif current == ORANGE:
                    strip[i] = RED
                # If already red, keep red

            # Update the LED strip
            strip.show()

            # Pause briefly before the next iteration
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Stopping...")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate PyAudio
    p.terminate()

    # Clear the LED strip
    for i in range(LED_COUNT):
        strip[i] = OFF
    strip.show()

if __name__ == "__main__":
    get_audio_input()