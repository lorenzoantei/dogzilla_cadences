import time
import board
import neopixel

# Configurazione dei Neopixel
NUM_PIXELS = 24
pin = board.D18
ORDER = neopixel.RGB
BRIGHTNESS = 0.1
SPEED = 10

strip = neopixel.NeoPixel(pin, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False, pixel_order=ORDER)

# Definizione di una funzione che esegue l'effetto arcobaleno sui Neopixel
def rainbow(strip, wait):
    for z in range(3):
        for j in range(256):
            for i in range(NUM_PIXELS):
                color = wheel((i+j) & 255)
                strip[i] = color
            strip.show()
            time.sleep(wait / 1000.0)

# Funzione per calcolare il valore del colore in base alla posizione
def wheel(pos):
    pos = 255 - pos
    if pos < 85:
        return (255 - pos * 3, 0, pos * 3)
    elif pos < 170:
        pos -= 85
        return (0, pos * 3, 255 - pos * 3)
    else:
        pos -= 170
        return (pos * 3, 255 - pos * 3, 0)

# Esecuzione dell'effetto arcobaleno sui Neopixel
rainbow(strip, wait=SPEED)
