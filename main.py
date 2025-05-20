import pyaudio
import numpy as np
import time
import board
import neopixel
import collections

# LED strip configuration for NeoPixel
TOTAL_LEDS = 148
SEGMENT_SIZE = 74  # 74 LEDs per segment

# LED pins for the three strips
LED_PINS = [board.D18, board.D12, board.D21]

# Initialize the NeoPixel strips in a list
led_strips = [neopixel.NeoPixel(pin, TOTAL_LEDS, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB)
              for pin in LED_PINS]

prev_active = 0

def get_color_relative(i, active_count):
    if active_count == 0:
        return (0, 0, 0)
    cutoff = active_count / 3
    if i < cutoff:
        return (255, 0, 0)        # red
    elif i < 2 * cutoff:
        return (255, 75, 0)      # orange
    else:
        return (255, 225, 0)      # yellow

def build_led_colors(active_count):
    # Build colors for one 74-LED segment
    colors = []
    for i in range(SEGMENT_SIZE):
        if i < active_count:
            colors.append(get_color_relative(i, active_count))
        else:
            colors.append((0, 0, 0))
    # Second segment is the reverse of the first
    return colors + list(reversed(colors))

def update_leds_immediate(active_count):
    # Update all LED strips with the same colors
    full_colors = build_led_colors(active_count)
    for strip in led_strips:
        strip[:] = full_colors
        strip.show()
    print("Active LEDs per segment:", active_count)

def update_leds_animated(new_active):
    global prev_active
    if new_active != prev_active:
        old_colors = build_led_colors(prev_active)
        new_colors = build_led_colors(new_active)

        delta = abs(new_active - prev_active)
        # If fading out, use fixed number of steps and longer delay for a slower fade-out.
        if new_active < prev_active:
            steps = 20         # Fade-out slower, independent of delta
            step_delay = 0.05  # Longer delay for fade-out
        else:
            min_steps = 10
            steps = max(min_steps, delta + 1)
            step_delay = 0.015

        for step in range(steps):
            # Use cosine easing for a smooth fade
            t = (1 - np.cos(np.pi * step / (steps - 1))) / 2 if steps > 1 else 1
            blended_colors = []
            for old, new in zip(old_colors, new_colors):
                blended_colors.append((
                    int(old[0] * (1 - t) + new[0] * t),
                    int(old[1] * (1 - t) + new[1] * t),
                    int(old[2] * (1 - t) + new[2] * t)
                ))
            for strip in led_strips:
                strip[:] = blended_colors
                strip.show()
            time.sleep(step_delay)

        prev_active = new_active
        print("Active LEDs per segment:", new_active)

def turn_off_leds():
    for strip in led_strips:
        for i in range(SEGMENT_SIZE):
            strip[i] = (0, 0, 0)
            idx = TOTAL_LEDS - 1 - i
            strip[idx] = (0, 0, 0)
        strip.show()

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

MIN_RMS_THRESHOLD = 1000.0  # Only react to sounds louder than this value

# Define a maximum effective value (adjust based on your environment)
MAX_EFFECTIVE = 3000.0

# Parameters for our basic onset detection
HISTORY_SIZE = 10  # number of recent effective values to average
THRESHOLD_MULTIPLIER = 1.5  # how many times above the average to trigger
EXTRA_MINIMUM = 20.0  # additional absolute boost to avoid false triggers

energy_history = collections.deque(maxlen=HISTORY_SIZE)
gain = 3.0  # Amplification factor

try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)
        rms = np.sqrt(np.mean(np.square(samples)))
        peak = np.max(np.abs(samples))
        
        # Combine RMS and peak to capture transients
        effective = max(rms, peak / 1000.0)
        effective *= gain
        if np.isnan(effective):
            effective = 0.0

        # Update moving average (optional, if you still want to monitor trends)
        energy_history.append(effective)
        moving_avg = np.mean(energy_history) if energy_history else 0.0

        # Map the effective value to a number of active LEDs
        if effective < MIN_RMS_THRESHOLD:
            active_count = 0
        elif effective > MAX_EFFECTIVE:
            active_count = SEGMENT_SIZE
        else:
            active_count = int(((effective - MIN_RMS_THRESHOLD) / (MAX_EFFECTIVE - MIN_RMS_THRESHOLD)) * SEGMENT_SIZE)
        
        update_leds_animated(active_count)
        
        time.sleep(0.05)
except KeyboardInterrupt:
    pass

stream.stop_stream()
stream.close()
p.terminate()

turn_off_leds()
print("Stopped audio monitoring")

