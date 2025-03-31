import pyaudio
import numpy as np
import time
import board  # Required for neopixel
import adafruit_neopixel as neopixel  # Import the neopixel library

# Parameters
CHUNK = 1024  # Number of audio samples per frame
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Number of audio channels (1 for mono)
RATE = 44100  # Sample rate (samples per second)

# LED strip configuration:
LED_COUNT = 30        # Number of LED pixels.
LED_PIN =  board.D18  # GPIO pin connected to the pixels (D18 for PWM).
LED_BRIGHTNESS = 1.0  # Brightness (0.0 to 1.0)

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
            # Read audio data from the stream
            data = stream.read(CHUNK)
            # Convert the data to numpy array
            audio_data = np.frombuffer(data, dtype=np.int16)
            # Calculate the volume (RMS)
            volume = np.sqrt(np.mean(audio_data**2))
            print(f"Volume: {volume}")

            # Perform actions based on volume
            if volume > 50:
                print("Sound detected!")
                color = (255, 0, 0)  # Red color for high volume
            else:
                print("Sound is quiet.")
                color = (0, 0, 255)  # Blue color for low volume

            # Set LED color based on volume
            for i in range(LED_COUNT):
                strip[i] = color
            strip.show()

            time.sleep(0.1)  # Add a slight delay of 0.1 seconds

    except KeyboardInterrupt:
        print("Stopping...")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate PyAudio
    p.terminate()

    # Clear the LED strip
    strip.fill((0, 0, 0))
    strip.show()

if __name__ == "__main__":
    get_audio_input()