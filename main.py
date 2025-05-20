import pyaudio
import numpy as np
import time
import board
import neopixel

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
        
        # Use a minimum number of steps for small transitions for smoother animation
        delta = abs(new_active - prev_active)
        min_steps = 10
        steps = max(min_steps, delta + 1)
        
        for step in range(steps):
            # Cosine easing for a smooth ease-in, ease-out effect
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
            time.sleep(0.015)  # adjust delay as needed for smoothness
        
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

MIN_RMS_THRESHOLD = 30.0  # Only react to sounds louder than this value

try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        samples = np.frombuffer(data, dtype=np.int16)
        rms = np.sqrt(np.mean(np.square(samples)))
        peak = np.max(np.abs(samples))
        
        # Combine RMS and peak to better capture transients like a break
        effective = max(rms, peak / 1000.0)
        
        # Amplify the effective value to boost transient response
        gain = 3.0  # Increase this value if needed
        effective *= gain
        
        if np.isnan(effective):
            effective = 0.0
        
        max_effective = 300.0   # Adjust as needed for your mic's range
        if effective < MIN_RMS_THRESHOLD:
            active_count = 0
        else:
            # Scale the response so that only sounds above the threshold trigger LEDs
            normalized = (effective - MIN_RMS_THRESHOLD) / (max_effective - MIN_RMS_THRESHOLD)
            factor = normalized ** 1.5  # Exponent enhances response to louder/thumpier sounds
            active_count = int(factor * SEGMENT_SIZE)
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

