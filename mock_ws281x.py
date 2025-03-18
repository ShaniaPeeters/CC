# filepath: c:\school\2425\CC\Groep4\mock_ws281x.py
class PixelStrip:
    def __init__(self, num, pin, freq_hz, dma, invert, brightness, channel):
        self.num = num
        self.pixels = [(0, 0, 0)] * num

    def begin(self):
        print("Mock LED strip initialized.")

    def setPixelColor(self, n, color):
        self.pixels[n] = color

    def show(self):
        print(f"LEDs updated: {self.pixels}")

    def numPixels(self):
        return self.num

def Color(r, g, b):
    return (r, g, b)