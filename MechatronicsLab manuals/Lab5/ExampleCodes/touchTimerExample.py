from arduino import start, delay
from arduino_alvik import ArduinoAlvik

# Global variables
blink_period = 500   # initial period in ms
toggle_value_gen = None  # will store a generator instance

alvik = ArduinoAlvik()

def toggle_value():
    """
    Generator that returns 0,1,0,1,... each time next() is called.
    """
    value = 0
    while True:
        yield value % 2
        value += 1

def blink_left_led(*args):
    """
    Callback for the timer: toggles the left LED's red channel on/off
    every time the timer fires. Uses the global 'toggle_value_gen'
    and 'blink_period' to show the current timing.
    """
    global blink_period, toggle_value_gen

    led_val = next(toggle_value_gen)  # 0 or 1
    alvik.left_led.set_color(led_val, 0, 0)
    print(f"Blink! LED is now {'ON' if led_val else 'OFF'} - Period: {blink_period} ms")

def setup():
    global blink_period, toggle_value_gen

    # 1) Create the toggle generator
    toggle_value_gen = toggle_value()

    # 2) Register a periodic timer at blink_period ms to call 'blink_left_led'
    #    We don't need to pass arguments if our callback references the global generator
    alvik.set_timer('periodic', blink_period, blink_left_led, ())

    # 3) Initialize Alvik
    alvik.begin()
    delay(500)

    print("Touch-based Timer Example:")
    print(" - UP arrow  : +100 ms to blink period")
    print(" - DOWN arrow: -100 ms to blink period")
    print(" - OK        : RESUME the timer")
    print(" - CANCEL    : STOP the timer")

    delay(500)

def loop():
    global blink_period

    # Check for any touch input
    if alvik.get_touch_any():
        # Increase period by 100 ms on UP press
        if alvik.get_touch_up():
            blink_period += 100
            alvik.timer.reset(period=blink_period)
            print(f"UP pressed => New period: {blink_period} ms")

        # Decrease period by 100 ms on DOWN press
        if alvik.get_touch_down():
            # Ensure we don't go below a certain threshold (100 ms)
            if blink_period > 100:
                blink_period -= 100
                alvik.timer.reset(period=blink_period)
                print(f"DOWN pressed => New period: {blink_period} ms")
            else:
                print("Cannot reduce period below 100 ms.")

        # OK => RESUME the timer
        if alvik.get_touch_ok():
            alvik.timer.resume()
            print("Timer RESUMED.")

        # CANCEL => STOP the timer
        if alvik.get_touch_cancel():
            alvik.timer.stop()
            print("Timer STOPPED.")

    # Small delay to avoid spamming
    delay(100)

def cleanup():
    print("Cleaning up: Stopping the timer & Alvik.")
    alvik.timer.stop()
    alvik.stop()

# Start the program
start(setup, loop, cleanup)
