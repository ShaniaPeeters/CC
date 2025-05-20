import pyaudio
import numpy as np
import time
import board
import neopixel

# LED strip configuration for NeoPixel
TOTAL_LEDS = 148
SEGMENT_SIZE = 74  # 74 LEDs per segment
LED_PIN = board.D18  # Change this if your LED strip is connected to a different pin

# Initialize the NeoPixel strip
pixels = neopixel.NeoPixel(LED_PIN, TOTAL_LEDS, brightness=0.2, auto_write=False)

# Global variable to track the current number of lit LEDs per segment.
prev_active = 0

def update_leds_immediate(active_count):
    # This function immediately updates all LEDs according to active_count.
    for i in range(SEGMENT_SIZE):
        if i < active_count:
            color = (255, 0, 0)
        else:
            color = (0, 0, 0)
        pixels[i] = color

    for i in range(SEGMENT_SIZE):
        idx = TOTAL_LEDS - 1 - i
        if i < active_count:
            color = (255, 0, 0)
        else:
            color = (0, 0, 0)
        pixels[idx] = color

    pixels.show()
    print("Active LEDs per segment:", active_count)

def update_leds_animated(new_active):
    global prev_active

    # Animate increasing count: light up additional LEDs one at a time.
    if new_active > prev_active:
        for i in range(prev_active, new_active):
            pixels[i] = (255, 0, 0)
            idx = TOTAL_LEDS - 1 - i
            pixels[idx] = (255, 0, 0)
            pixels.show()
            time.sleep(0.01)
    # Animate decreasing count: turn off LEDs one at a time.
    elif new_active < prev_active:
        for i in range(prev_active - 1, new_active - 1, -1):
            pixels[i] = (0, 0, 0)
            idx = TOTAL_LEDS - 1 - i
            pixels[idx] = (0, 0, 0)
            pixels.show()
            time.sleep(0.01)
    prev_active = new_active
    print("Active LEDs per segment:", new_active)

def turn_off_leds():
    # Turn off all LEDs in both segments.
    for i in range(SEGMENT_SIZE):
        pixels[i] = (0, 0, 0)
        idx = TOTAL_LEDS - 1 - i
        pixels[idx] = (0, 0, 0)
    pixels.show()

# Audio stream configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Monitoring audio... Press Ctrl+C to stop.")

try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        samples = np.frombuffer(data, dtype=np.int16)
        # Calculate the RMS volume of the input audio
        rms = np.sqrt(np.mean(np.square(samples)))
        if np.isnan(rms):
            rms = 0.0
        
        # Map the RMS value to the number of LEDs to light per segment.
        max_rms = 3000.0  # example value, adjust as necessary
        active_count = int((rms / max_rms) * SEGMENT_SIZE)
        active_count = min(active_count, SEGMENT_SIZE)  # clamp to maximum
        
        # Animate LED changes incrementally.
        update_leds_animated(active_count)
        time.sleep(0.05)
except KeyboardInterrupt:
    pass

stream.stop_stream()
stream.close()
p.terminate()

# Turn off LEDs before exiting.
turn_off_leds()
print("Stopped audio monitoring")

