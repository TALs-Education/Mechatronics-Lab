from arduino import start, delay
from arduino_alvik import ArduinoAlvik

alvik = ArduinoAlvik()

def setup():
    # 1) Initialize Alvik
    alvik.begin()
    delay(1000)  # small delay

def loop():
    # 2) Check if any touch sensor is activated
    if alvik.get_touch_any():
        # Check each possible direction/button
        if alvik.get_touch_up():
            print("UP")
        if alvik.get_touch_down():
            print("DOWN")
        if alvik.get_touch_left():
            print("LEFT")
        if alvik.get_touch_right():
            print("RIGHT")
        if alvik.get_touch_ok():
            print("OK")
        if alvik.get_touch_cancel():
            print("CANCEL")
        if alvik.get_touch_center():
            print("CENTER")

    # 3) Delay 100ms before checking again
    delay(100)

def cleanup():
    print("Exiting touch example...")
    alvik.stop()

# Start the Arduino-like main loop
start(setup, loop, cleanup)
