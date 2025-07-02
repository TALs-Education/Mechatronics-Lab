from arduino import start, delay
from arduino_alvik import ArduinoAlvik

# Import library with font, buffer, set_pixel, etc.
import mysimple_oled as oled

# We'll define our own write functions here for I2C
def ssd1306_command(i2c, cmd):
    """Send a single command byte (0x00 control)."""
    i2c.writeto(oled.OLED_I2C_ADDR, b"\x00" + bytes([cmd]))

def ssd1306_commands(i2c, cmd_list):
    """Send multiple command bytes in one go."""
    i2c.writeto(oled.OLED_I2C_ADDR, b"\x00" + bytes(cmd_list))

def ssd1306_init(i2c):
    """Init the display at 0x3D for 128x64."""
    cmds = [
        0xAE,         # DISPLAYOFF
        0xD5, 0x80,   # SETDISPLAYCLOCKDIV
        0xA8, 0x3F,   # SETMULTIPLEX
        0xD3, 0x00,   # SETDISPLAYOFFSET
        0x40,         # SETSTARTLINE
        0x8D, 0x14,   # CHARGEPUMP on
        0x20, 0x00,   # MEMORYMODE horizontal
        0xA1,         # SEGREMAP
        0xC8,         # COMSCANDEC
        0xDA, 0x12,   # SETCOMPINS
        0x81, 0x7F,   # SETCONTRAST
        0xD9, 0xF1,   # SETPRECHARGE
        0xDB, 0x40,   # SETVCOMDETECT
        0xA4,         # DISPLAYALLON_RESUME
        0xA6,         # NORMALDISPLAY
        0xAF          # DISPLAYON
    ]
    ssd1306_commands(i2c, cmds)

def ssd1306_show(i2c):
    """Write oled.oled_buffer to the physical display."""
    # columns 0..127
    ssd1306_commands(i2c, [0x21, 0x00, 0x7F])
    # pages 0..7
    ssd1306_commands(i2c, [0x22, 0x00, 0x07])

    chunk_size = 32
    idx = 0
    while idx < len(oled.oled_buffer):
        chunk = oled.oled_buffer[idx : idx + chunk_size]
        i2c.writeto(oled.OLED_I2C_ADDR, b"\x40" + chunk)
        idx += chunk_size

def ssd1306_fill(value):
    """Fill the buffer with a byte (0x00=off, 0xFF=on)."""
    for i in range(len(oled.oled_buffer)):
        oled.oled_buffer[i] = value

def setup():
    # Create Alvik + I2C
    global alvik
    alvik = ArduinoAlvik()
    alvik.begin()
    delay(500)

    # Init the display
    ssd1306_init(alvik.i2c)

    # Clear and show
    ssd1306_fill(0x00)
    ssd1306_show(alvik.i2c)

    # Draw "Hello World!" in the center using the library's draw_text
    text = "Hello World!"
    text_width = len(text) * 6
    x = (oled.OLED_WIDTH - text_width) // 2
    y = (oled.OLED_HEIGHT - 8) // 2  # 8 = font height
    oled.draw_text(x, y, text)
    ssd1306_show(alvik.i2c)

    print("Hello World displayed on OLED 0x3D")

def loop():
    # No special update, just keep the text
    delay(2000)

def cleanup():
    print("Clearing display, stopping.")
    ssd1306_fill(0)
    ssd1306_show(alvik.i2c)
    alvik.stop()

# Start the Arduino-like structure
start(setup, loop, cleanup)
