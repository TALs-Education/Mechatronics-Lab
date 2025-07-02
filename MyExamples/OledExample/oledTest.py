from arduino import *
from arduino_alvik import ArduinoAlvik

# -------------------------------------------------
# SSD1306 Minimal Driver for 128x64 at I2C addr 0x3C
# -------------------------------------------------

OLED_I2C_ADDR = 0x3d
OLED_WIDTH    = 128
OLED_HEIGHT   = 64
OLED_PAGES    = OLED_HEIGHT // 8  # 8 rows per page -> 8 pages total

# Framebuffer: 128 * 64 / 8 = 1024 bytes
oled_buffer = bytearray(OLED_WIDTH * OLED_PAGES)

alvik = ArduinoAlvik()

# ----------------------------------------
# Helper: Write a command over I2C
# ----------------------------------------
def ssd1306_command(cmd):
    """
    Sends a single command byte to the OLED.
    Control byte 0x00 means "next byte(s) are command(s)".
    """
    alvik.i2c.writeto(OLED_I2C_ADDR, b"\x00" + bytes([cmd]))

# ----------------------------------------
# Helper: Write multiple commands
# ----------------------------------------
def ssd1306_commands(cmd_list):
    """
    Sends multiple command bytes in one go.
    """
    alvik.i2c.writeto(OLED_I2C_ADDR, b"\x00" + bytes(cmd_list))

# ----------------------------------------
# Initialize the OLED
# ----------------------------------------
def ssd1306_init():
    """
    Minimal init sequence for a typical 128x64 SSD1306 in I2C mode.
    """
    commands = [
        0xAE,         # DISPLAYOFF
        0xD5, 0x80,   # SETDISPLAYCLOCKDIV
        0xA8, 0x3F,   # SETMULTIPLEX (0x3F = 63, for 64 rows)
        0xD3, 0x00,   # SETDISPLAYOFFSET
        0x40,         # SETSTARTLINE (line #0)
        0x8D, 0x14,   # CHARGEPUMP (enable)
        0x20, 0x00,   # MEMORYMODE (Horizontal Addressing Mode)
        0xA1,         # SEGREMAP (column address 127 is mapped to SEG0)
        0xC8,         # COMSCANDEC
        0xDA, 0x12,   # SETCOMPINS (0x12 for 128x64)
        0x81, 0x7F,   # SETCONTRAST
        0xD9, 0xF1,   # SETPRECHARGE
        0xDB, 0x40,   # SETVCOMDETECT
        0xA4,         # DISPLAYALLON_RESUME
        0xA6,         # NORMALDISPLAY
        0xAF          # DISPLAYON
    ]
    ssd1306_commands(commands)

# ----------------------------------------
# Write framebuffer to OLED
# ----------------------------------------
def ssd1306_show():
    """
    Updates the entire 128x64 display from our 'oled_buffer'.
    We set the column and page addresses, then write data.
    """
    # 1) Set column address to 0..127
    ssd1306_commands([0x21, 0x00, 0x7F])
    # 2) Set page address to 0..7
    ssd1306_commands([0x22, 0x00, 0x07])

    # 3) Send buffer in chunks. Control byte 0x40 means "next bytes are data".
    #    We can only send ~30 bytes at a time (depending on I2C buffer), so chunk it.
    chunk_size = 32
    for i in range(0, len(oled_buffer), chunk_size):
        chunk = oled_buffer[i : i + chunk_size]
        alvik.i2c.writeto(OLED_I2C_ADDR, b"\x40" + chunk)

# ----------------------------------------
# Clear the buffer
# ----------------------------------------
def ssd1306_fill(value):
    """
    Fill the entire buffer with 'value' (0x00 for all off, 0xFF for all on).
    For a pattern, you'd manually set bits in the buffer.
    """
    for i in range(len(oled_buffer)):
        oled_buffer[i] = value

# -----------------------------------------------------------------
# Example: animate a horizontal bar across the screen
# -----------------------------------------------------------------
bar_x = 0  # We'll move this "bar" from left to right

def setup():
    print("Initializing Alvik & OLED...")

    # 1) Alvik init
    alvik.begin()
    delay(500)

    # 2) Start I2C scanning (optional)
    devices = alvik.i2c.scan()
    print("I2C devices found:", [hex(d) for d in devices])

    # 3) Initialize the SSD1306
    ssd1306_init()
    delay(500)

    # Clear the buffer
    ssd1306_fill(0x00)
    # Show initial blank screen
    ssd1306_show()
    print("OLED initialized and blank.")


def loop():
    global bar_x

    # 1) Clear the buffer each frame
    ssd1306_fill(0x00)

    # 2) Draw a vertical bar 8px wide from top to bottom at x=bar_x
    #    For a 128x64 display, that's 8 pages if you consider each page 8 bits tall.
    #    We'll set bits in the buffer for that region.
    bar_width = 8

    # pages = 8 total (0..7)
    # each page has 128 bytes
    # buffer index = page*128 + column
    for col in range(bar_x, bar_x + bar_width):
        if 0 <= col < OLED_WIDTH:
            for page in range(OLED_PAGES):
                # Each page holds 8 vertical bits
                # We want all bits "on" = 0xFF
                idx = page * OLED_WIDTH + col
                oled_buffer[idx] = 0xFF

    # 3) Send buffer to the display
    ssd1306_show()

    # 4) Update bar_x
    bar_x = (bar_x + 2) % OLED_WIDTH

    # 5) Small delay so it doesn't move too fast
    delay(50)

def cleanup():
    print("Stopping Alvik & clearing display.")
    ssd1306_fill(0x00)
    ssd1306_show()
    alvik.stop()


# -----------------------------------------------------------------
# "Arduino-like" entry point
# -----------------------------------------------------------------
start(setup, loop, cleanup)
