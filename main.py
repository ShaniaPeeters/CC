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
pixels = neopixel.NeoPixel(LED_PIN, TOTAL_LEDS, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB)

prev_active = 0

def get_color_relative(i, active_count):
    if active_count == 0:
        return (0,0,0)
    cutoff = active_count / 3
    if i < cutoff:
        return (255, 0, 0)        # red
    elif i < 2 * cutoff:
        return (255, 75, 0)      # orange
    else:
        return (255, 225, 0)      # yellow

def build_led_colors(active_count):
    # Build colors for one segment
    colors = []
    for i in range(SEGMENT_SIZE):
        if i < active_count:
            colors.append(get_color_relative(i, active_count))
        else:
            colors.append((0, 0, 0))
    # Second segment is the reverse of the first
    return colors + list(reversed(colors))

def update_leds_immediate(active_count):
    # For each segment, light the first active_count LEDs with
    # a smooth gradient based on their relative index.
    for i in range(SEGMENT_SIZE):
        if i < active_count:
            color = get_color_relative(i, active_count)
        else:
            color = (0, 0, 0)
        pixels[i] = color

    for i in range(SEGMENT_SIZE):
        idx = TOTAL_LEDS - 1 - i
        if i < active_count:
            color = get_color_relative(i, active_count)
        else:
            color = (0, 0, 0)
        pixels[idx] = color

    pixels.show()
    print("Active LEDs per segment:", active_count)

def update_leds_animated(new_active):
    global prev_active
    if new_active != prev_active:
        # Precompute the final state gradient using new_active
        final_colors = build_led_colors(new_active)
        step = 1 if new_active > prev_active else -1
        for active in range(prev_active, new_active, step):
            temp_segment = []
            # Build a temporary segment using the precomputed final color
            # for indices that should be lit and off for others.
            for i in range(SEGMENT_SIZE):
                temp_segment.append(final_colors[i] if i < active else (0, 0, 0))
            full_colors = temp_segment + list(reversed(temp_segment))
            # Update the full LED buffer at once
            pixels[:] = full_colors
            pixels.show()
            time.sleep(0.01)  # adjust delay as needed
        # Set the final LED state
        pixels[:] = final_colors
        pixels.show()
        prev_active = new_active
        print("Active LEDs per segment:", new_active)

def turn_off_leds():
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
        rms = np.sqrt(np.mean(np.square(samples)))
        if np.isnan(rms):
            rms = 0.0
        
        max_rms = 100.0   # adjust as necessary
        active_count = int((rms / max_rms) * SEGMENT_SIZE)
        active_count = min(active_count, SEGMENT_SIZE)
        
        update_leds_animated(active_count)
        time.sleep(0.05)
except KeyboardInterrupt:
    pass

stream.stop_stream()
stream.close()
p.terminate()

turn_off_leds()
print("Stopped audio monitoring")

