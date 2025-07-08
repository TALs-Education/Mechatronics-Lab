from arduino import start, delay
from arduino_alvik import ArduinoAlvik
from time import sleep_ms, ticks_ms

# === CONFIG ===
FORWARD_SPEED = 100     # max wheel speed (–100…100)
TURN_SPEED    = 50      # moderate turning speed
TOGGLE_INTERVAL = 2000  # ms for backward alternating

# === SETUP ===
alvik = ArduinoAlvik()

def setup():
    alvik.begin()
    # Center servos (so “stop” = neutral)
    alvik.servo_A.set_position(90)
    alvik.servo_B.set_position(90)

# === MAIN LOOP ===
def loop():
    global last_toggle, back_dir

    # Initialize toggle state on first pass
    if 'last_toggle' not in globals():
        last_toggle = ticks_ms()
        back_dir     = True

    # --- FORWARD: both wheels & servos at full speed ---
    if alvik.get_touch_up():
        alvik.move(FORWARD_SPEED, blocking=False)
        alvik.servo_A.set_position(180)
        alvik.servo_B.set_position(180)

    # --- STOP/CENTER: coast/brake wheels & neutral servos ---
    elif alvik.get_touch_center():
        alvik.brake()
        alvik.servo_A.set_position(90)
        alvik.servo_B.set_position(90)

    # --- LEFT TURN: gradual turn at moderate speed ---
    elif alvik.get_touch_left():
        alvik.move(TURN_SPEED, blocking=False)
        # example of differential servo action for left skid-turn
        alvik.servo_A.set_position(110)  # servo A pushes forward
        alvik.servo_B.set_position(70)   # servo B pushes backward

    # --- RIGHT TURN: gradual turn at moderate speed ---
    elif alvik.get_touch_right():
        alvik.move(-TURN_SPEED, blocking=False)
        alvik.servo_A.set_position(70)
        alvik.servo_B.set_position(110)

    # --- BACKWARD: full speed with direction flip every 2 s ---
    elif alvik.get_touch_down():
        now = ticks_ms()
        if now - last_toggle > TOGGLE_INTERVAL:
            back_dir     = not back_dir
            last_toggle  = now
        speed = -FORWARD_SPEED if back_dir else FORWARD_SPEED
        alvik.move(speed, blocking=False)
        # servo positions flip between extremes
        alvik.servo_A.set_position(180 if back_dir else 0)
        alvik.servo_B.set_position(180 if back_dir else 0)

    # --- NO BUTTON: safe idle ---
    else:
        alvik.brake()
        alvik.servo_A.set_position(90)
        alvik.servo_B.set_position(90)

    sleep_ms(50)


# === RUN ===
start(setup, loop)
