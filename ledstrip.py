import time
import board
import neopixel

# Color definitions
YELLOW = (255, 230, 0)  # yellow with less green
ORANGE = (255, 50, 0)   # modified: way more orange
RED    = (255, 0, 0)
OFF    = (0, 0, 0)

class LEDStrip:
    def __init__(self, pin, num_leds, brightness):
        self.strip = neopixel.NeoPixel(pin, num_leds, brightness=brightness, auto_write=False)
        self.led_count = num_leds
        self.last_update = [time.time() for _ in range(num_leds)]

    def initialize(self):
        # Set all LEDs to white, wait, then turn them off
        self.strip.fill((255, 255, 255))
        self.strip.show()
        time.sleep(1)
        self.strip.fill(OFF)
        self.strip.show()

    def update_leds(self, trigger_count):
        transitions = 0
        count = 0
        i = 0
        while count < trigger_count and i < self.led_count:
            if tuple(self.strip[i]) == RED:
                i += 1
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
            self.last_update[i] = time.time()
            if change in ["YELLOW to ORANGE", "ORANGE to RED"]:
                transitions += 1
            count += 1
            i += 1
        return transitions

    def propagate(self, trigger_count, transitions):
        j = trigger_count - 1
        while j >= 0 and transitions > 0:
            if tuple(self.strip[j]) == OFF:
                self.strip[j] = YELLOW
                self.last_update[j] = time.time()
                transitions -= 1
            j -= 1

    def fade(self, fade_delay):
        current_time = time.time()
        for i in range(self.led_count - 1, -1, -1):
            if current_time - self.last_update[i] > fade_delay:
                current = tuple(self.strip[i])
                if current == RED:
                    self.strip[i] = ORANGE
                    self.last_update[i] = current_time
                    break
                elif current == ORANGE:
                    self.strip[i] = YELLOW
                    self.last_update[i] = current_time
                    break
                elif current == YELLOW:
                    self.strip[i] = OFF
                    self.last_update[i] = current_time
                    break

    def clear(self):
        for i in range(self.led_count):
            self.strip[i] = OFF
        self.strip.show()

    def show(self):
        self.strip.show()
