from arduino import start, delay
from arduino_alvik import ArduinoAlvik

def toggle_value():
    """
    Generator that toggles values 0,1,0,1,... each time next() is called.
    """
    value = 0
    while True:
        yield value % 2
        value += 1

def toggle_left_led(custom_text: str, val) -> None:
    """
    Toggle the left LED's red channel on/off. Print custom text.
    :param custom_text: A string to display
    :param val: A toggle-value generator
    """
    led_val = next(val)
    alvik.left_led.set_color(led_val, 0, 0)
    print(f"RED {'ON' if led_val else 'OFF'}! {custom_text}")

def simple_print(custom_text: str = '') -> None:
    print(custom_text)

# Create Alvik instance
alvik = ArduinoAlvik()

def setup():
    # Register the on_shake callback before starting
    alvik.on_shake(toggle_left_led, ("ALVIK WAS SHAKEN...:)", toggle_value(), ))
    
    # Initialize Alvik
    alvik.begin()
    delay(500)

def loop():
    # Print distance every 2 seconds
    distance = alvik.get_distance()
    print(distance)
    delay(2000)

def cleanup():
    print("Shaken script over.")
    alvik.stop()

# Start the Arduino-like structure
start(setup, loop, cleanup)
