from arduino import start, delay
from arduino_alvik import ArduinoAlvik

alvik = ArduinoAlvik()

def setup():
    # Initialize the Alvik board
    alvik.begin()
    delay(1000)  # small delay after init

def loop():
    # Read accelerations (ax, ay, az)
    ax, ay, az = alvik.get_accelerations()
    
    # Read gyros (gx, gy, gz)
    gx, gy, gz = alvik.get_gyros()
    
    # Print them to the console
    print(f"ax: {ax}, ay: {ay}, az: {az}, gx: {gx}, gy: {gy}, gz: {gz}")
    
    # Wait 100ms before next reading
    delay(100)

def cleanup():
    # Called once when script stops or ctrl+c
    print("Stopping Alvik...")
    alvik.stop()

# Start the Arduino-like main loop
start(setup, loop, cleanup)