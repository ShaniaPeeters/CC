import time
import board
import neopixel

# Color definitions
YELLOW = (255, 216, 1)  # yellow with less green
ORANGE = (255, 50, 0)   # modified: way more orange
RED    = (255, 0, 0)
OFF    = (0, 0, 0)

class LEDStrip:
    def __init__(self, pin, total_leds, brightness, start=0, num_leds=None, reverse=False):
        # Create the underlying NeoPixel object.
        self.strip = neopixel.NeoPixel(pin, total_leds, brightness=brightness, auto_write=False)
        # If num_leds is not provided, control the whole strip.
        if num_leds is None:
            self.led_count = len(self.strip)
        else:
            self.led_count = num_leds
        self.reverse = reverse
        if not self.reverse:
            self.indices = list(range(start, start + self.led_count))
        else:
            # For reverse, count backwards starting from "start"
            self.indices = list(range(start, start - self.led_count, -1))
        # Create a last_update list mapped to the controlled segment order.
        self.last_update = [time.time() for _ in range(self.led_count)]

    def initialize(self):
        # Set all controlled LEDs to white, wait, then turn them off.
        for idx in range(self.led_count):
            self.strip[self.indices[idx]] = (255, 255, 255)
        self.strip.show()
        time.sleep(1)
        for idx in range(self.led_count):
            self.strip[self.indices[idx]] = OFF
        self.strip.show()

    def update_leds(self, trigger_count):
        if trigger_count <= 0:
            return 0
        transitions = 0
        # Iterate over the segment in its natural order (which reflects reverse if set).
        for i, led in enumerate(self.indices):
            # Skip if current LED is already fully red.
            if tuple(self.strip[led]) == RED:
                continue
            current = tuple(self.strip[led])
            if current == OFF:
                self.strip[led] = YELLOW
                change = "OFF to YELLOW"
            elif current == YELLOW:
                self.strip[led] = ORANGE
                change = "YELLOW to ORANGE"
            elif current == ORANGE:
                self.strip[led] = RED
                change = "ORANGE to RED"
            self.last_update[i] = time.time()
            if change in ["YELLOW to ORANGE", "ORANGE to RED"]:
                transitions = 1
            break  # only one LED changes per cycle
        return transitions

    def propagate(self, trigger_count, transitions):
        if trigger_count <= 0 or transitions <= 0:
            return
        # Iterate over the segment in the reverse order of the configured indices.
        for i in range(self.led_count - 1, -1, -1):
            led = self.indices[i]
            if tuple(self.strip[led]) == OFF:
                self.strip[led] = YELLOW
                self.last_update[i] = time.time()
                break  # only update one LED

    def fade(self, fade_delay):
        current_time = time.time()
        # Iterate over the segment in the reverse order.
        for i in range(self.led_count - 1, -1, -1):
            led = self.indices[i]
            if current_time - self.last_update[i] > fade_delay:
                current = tuple(self.strip[led])
                if current == RED:
                    self.strip[led] = ORANGE
                    self.last_update[i] = current_time
                    break  # only one LED fades per cycle
                elif current == ORANGE:
                    self.strip[led] = YELLOW
                    self.last_update[i] = current_time
                    break
                elif current == YELLOW:
                    self.strip[led] = OFF
                    self.last_update[i] = current_time
                    break

    def clear(self):
        for i in range(self.led_count):
            self.strip[self.indices[i]] = OFF
        self.strip.show()

    def show(self):
        self.strip.show()
