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
LED_PIN = board.D18      # GPIO pin connected to the pixels (D18 for PWM).
LED_BRIGHTNESS = 1.0     # Brightness (0.0 to 1.0)

# Color definitions
YELLOW = (255, 230, 0)  # modified: yellow with less green
ORANGE = (255, 140, 0)  # modified: more vivid orange
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

    # Initialize LED strip with a hard-coded count for creation; then count leds dynamically
    strip = neopixel.NeoPixel(LED_PIN, 100, brightness=LED_BRIGHTNESS, auto_write=False)
    LED_COUNT = len(strip)  # Count number of LEDs dynamically

    # Set all LEDs to white, keep them on for 1 second, then turn them off
    strip.fill((255, 255, 255))  # Set all LEDs to white
    strip.show()
    time.sleep(1)  # Keep them on for 1 second
    strip.fill(OFF)  # Turn them off
    strip.show()

    # Initialize LED update timestamps and fade delay (in seconds)
    last_update = [time.time() for _ in range(LED_COUNT)]
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

            # Convert data to numpy array and calculate volume (RMS)
            audio_data = np.frombuffer(data, dtype=np.int16)
            volume = np.sqrt(np.mean(audio_data**2))
            volume = np.nan_to_num(volume)  # Convert NaN to 0 if encountered
            print(f"Volume: {volume}")

            # Determine how many LEDs to trigger.
            # Set a minimum threshold and a maximum volume for scaling.
            min_volume = 60    # volume to start triggering LEDs
            max_volume = 100  # volume at which all LEDs are triggered

            if volume < min_volume:
                trigger_count = 0
            else:
                # Scale linearly from 1 LED at min_volume to LED_COUNT at max_volume
                trigger_count = min(LED_COUNT, 1 + int((volume - min_volume) * (LED_COUNT - 1) / (max_volume - min_volume)))
            print(f"Triggering {trigger_count} LEDs")

            # For the triggered LEDs, update color based on current state.
            transition_total = 0  # count of transitions needing propagation
            for i in range(trigger_count):
                original = tuple(strip[i])
                print(f"Triggering LED {i}, current: {original}")
                if original == OFF:
                    strip[i] = YELLOW
                    change = "OFF to YELLOW"
                elif original == YELLOW:
                    strip[i] = ORANGE
                    change = "YELLOW to ORANGE"
                elif original == ORANGE:
                    strip[i] = RED
                    change = "ORANGE to RED"
                print(f"LED {i} updated to: {strip[i]} (transition {change})")
                last_update[i] = time.time()
                if change in ["YELLOW to ORANGE", "ORANGE to RED"]:
                    transition_total += 1

            # Propagate additional yellows based on total transitions from YELLOW->ORANGE or ORANGE->RED.
            j = trigger_count - 1  # start searching from the highest triggered index downward
            while j >= 0 and transition_total > 0:
                if tuple(strip[j]) == OFF:
                    strip[j] = YELLOW
                    last_update[j] = time.time()
                    print(f"Propagating: lighting LED {j} to YELLOW (additional propagation)")
                    transition_total -= 1
                j -= 1

            # Fade LEDs from the farthest end towards the source if not updated recently:
            current_time = time.time()
            for i in range(LED_COUNT - 1, -1, -1):
                if current_time - last_update[i] > fade_delay:
                    current_color = tuple(strip[i])
                    if current_color == RED:
                        strip[i] = ORANGE
                        last_update[i] = current_time
                        print(f"Fading LED {i} from RED to ORANGE")
                        break
                    elif current_color == ORANGE:
                        strip[i] = YELLOW
                        last_update[i] = current_time
                        print(f"Fading LED {i} from ORANGE to YELLOW")
                        break
                    elif current_color == YELLOW:
                        strip[i] = OFF
                        last_update[i] = current_time
                        print(f"Fading LED {i} from YELLOW to OFF")
                        break  # Fade only one LED per cycle

            strip.show()
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