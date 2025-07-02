from arduino import start, delay
from arduino_alvik import ArduinoAlvik

def toggle_value():
    """
    A generator that yields 0,1,0,1,... each time 'next()' is called.
    """
    value = 0
    while True:
        yield value % 2
        value += 1

def toggle_left_led(custom_text: str, val) -> None:
    """
    Toggles the left LED's red channel on/off, printing 'custom_text'.
    
    :param custom_text: Some text to display each time it toggles
    :param val: A toggle generator that returns 0 or 1
    """
    led_val = next(val)
    alvik.left_led.set_color(led_val, 0, 0)
    print(f"RED {'ON' if led_val else 'OFF'}! {custom_text}")

# Create the Alvik object
alvik = ArduinoAlvik()

def setup():
    # 1) Register a periodic timer at 500 ms to call 'toggle_left_led'
    #    Pass in a tuple of arguments: custom_text + the toggle_value() generator
    alvik.set_timer('periodic', 500, toggle_left_led, ("500 ms have passed...", toggle_value(), ))

    # 2) Initialize Alvik
    alvik.begin()
    delay(500)

def loop():
    # Nothing else to do; the timer runs in the background
    delay(500)

def cleanup():
    print("User stopped the script.")
    alvik.stop()

# Start the Arduino-like loop structure
start(setup, loop, cleanup)
