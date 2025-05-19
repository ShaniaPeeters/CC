import time
import board
import neopixel

# Color definitions
YELLOW = (255, 216, 1)  # yellow with less green
ORANGE = (255, 50, 0)   # modified: way more orange
RED    = (255, 0, 0)
OFF    = (0, 0, 0)

class LEDStrip:
    def __init__(self, pin, start_led, num_leds, brightness, reverse):
        self.strip = neopixel.NeoPixel(pin, num_leds*2, brightness=brightness, auto_write=False)
        self.led_count = num_leds # dynamically determine LED count from the neopixel object
        self.last_update = [time.time() for _ in range(self.led_count)]
        self.start_led = start_led

    def initialize(self):
        # Set all LEDs to white, wait, then turn them off
        self.strip.fill((255, 255, 255))
        self.strip.show()
        time.sleep(1)
        self.strip.fill(OFF)
        self.strip.show()

    def update_leds(self, trigger_count):
        if trigger_count <= 0:
            return 0
        transitions = 0
        for ix in range(self.led_count):
            i = ix + self.start_led
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
            self.last_update[i] = time.time()
            if change in ["YELLOW to ORANGE", "ORANGE to RED"]:
                transitions = 1
            break  # only one LED changes per cycle
        return transitions

    def propagate(self, trigger_count, transitions):
        if trigger_count <= 0 or transitions <= 0:
            return
        for j in range(trigger_count - 1, -1, -1):
            if tuple(self.strip[j]) == OFF:
                self.strip[j] = YELLOW
                self.last_update[j] = time.time()
                break  # only update one LED

    def fade(self, fade_delay):
        current_time = time.time()
        for i in range(self.led_count - 1, -1, -1):
            if current_time - self.last_update[i] > fade_delay:
                current = tuple(self.strip[i])
                if current == RED:
                    self.strip[i] = ORANGE
                    self.last_update[i] = current_time
                    break  # only one LED fades per cycle
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
