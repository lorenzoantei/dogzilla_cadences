import board
import neopixel

NUM_LEDS = 24
PIN = board.D18

strip = neopixel.NeoPixel(PIN, NUM_LEDS)

strip.fill((0, 0, 0))
strip.show
