import time
import board
import neopixel

# Color definitions
YELLOW = (255, 216, 1)  # yellow with less green
ORANGE = (255, 50, 0)   # modified: way more orange
RED    = (255, 0, 0)
OFF    = (0, 0, 0)

class LEDStrip:
    def __init__(self, pin, total_leds, brightness, start=0, num_leds=None):
        # Create the underlying NeoPixel object.
        self.strip = neopixel.NeoPixel(pin, total_leds, brightness=brightness, auto_write=False)
        # If num_leds is not provided, control the whole strip.
        if num_leds is None:
            self.start = 0
            self.led_count = len(self.strip)
        else:
            self.start = start
            self.led_count = num_leds
        # Create a last_update list for the segment.
        self.last_update = [time.time() for _ in range(self.led_count)]

    def initialize(self):
        # Set all controlled LEDs to white, wait, then turn them off.
        for idx in range(self.led_count):
            self.strip[self.start + idx] = (255, 255, 255)
        self.strip.show()
        time.sleep(1)
        for idx in range(self.led_count):
            self.strip[self.start + idx] = OFF
        self.strip.show()

    def update_leds(self, trigger_count):
        if trigger_count <= 0:
            return 0
        transitions = 0
        for idx in range(self.led_count):
            i = self.start + idx
            # Skip if current LED is already fully red
            if tuple(self.strip[i]) == RED:
                continue
            current = tuple(self.strip[i])
            if current == OFF:
                self.strip[i] = YELLOW
                change = "OFF to YELLOW"
            elif current == YELLOW:
                self.strip[i] = ORANGE
                change = "YELLOW to ORANGE"
            elif current == ORANGE:
                self.strip[i] = RED
                change = "ORANGE to RED"
            self.last_update[idx] = time.time()
            if change in ["YELLOW to ORANGE", "ORANGE to RED"]:
                transitions = 1
            break  # only one LED changes per cycle
        return transitions

    def propagate(self, trigger_count, transitions):
        if trigger_count <= 0 or transitions <= 0:
            return
        for idx in range(self.led_count - 1, -1, -1):
            i = self.start + idx
            if tuple(self.strip[i]) == OFF:
                self.strip[i] = YELLOW
                self.last_update[idx] = time.time()
                break  # only update one LED

    def fade(self, fade_delay):
        current_time = time.time()
        for idx in range(self.led_count - 1, -1, -1):
            i = self.start + idx
            if current_time - self.last_update[idx] > fade_delay:
                current = tuple(self.strip[i])
                if current == RED:
                    self.strip[i] = ORANGE
                    self.last_update[idx] = current_time
                    break  # only one LED fades per cycle
                elif current == ORANGE:
                    self.strip[i] = YELLOW
                    self.last_update[idx] = current_time
                    break
                elif current == YELLOW:
                    self.strip[i] = OFF
                    self.last_update[idx] = current_time
                    break

    def clear(self):
        for idx in range(self.led_count):
            self.strip[self.start + idx] = OFF
        self.strip.show()

    def show(self):
        self.strip.show()
