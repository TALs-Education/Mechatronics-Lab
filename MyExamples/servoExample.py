from arduino import *
from arduino_alvik import ArduinoAlvik

alvik = ArduinoAlvik()

# We'll keep a global variable 'i' to track the servo angle
i = 0

def setup():
    alvik.begin()
    delay(1000)  # small delay after initialization

def loop():
    global i

    # Move both servos (A & B) to the same position i
    alvik.servo_A.set_position(i)
    alvik.servo_B.set_position(i)

    # Increment i, wrapping around at 180 degrees
    i = (i + 1) % 180

    # Small delay so movement isn't too fast
    delay(10)

def cleanup():
    alvik.stop()

# Start the program
start(setup, loop, cleanup)