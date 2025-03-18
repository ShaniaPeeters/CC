import pyaudio
import numpy as np
import time  # Import time for delay
from mock_ws281x import PixelStrip, Color  # Import the library for WS2812B LEDs
# from rpi_ws281x import PixelStrip, Color  # Uncomment this line when running on Raspberry Pi

# Parameters
CHUNK = 1024  # Number of audio samples per frame
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Number of audio channels (1 for mono)
RATE = 44100  # Sample rate (samples per second)

# LED strip configuration:
LED_COUNT = 30        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # Set to 1 for GPIOs 13, 19, 41, 45 or 53

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
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

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
                color = Color(255, 0, 0)  # Red color for high volume
            else:
                print("Sound is quiet.")
                color = Color(0, 0, 255)  # Blue color for low volume

            # Set LED color based on volume
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, color)
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
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

if __name__ == "__main__":
    get_audio_input()