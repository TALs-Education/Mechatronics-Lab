"""
mysimple_oled.py
----------------
Holds only the font definitions, a framebuffer for 128×64,
and helper functions to draw into that buffer (no I2C code).
"""

# Public constants for display geometry
OLED_WIDTH    = 128
OLED_HEIGHT   = 64
OLED_PAGES    = OLED_HEIGHT // 8  # 8 vertical pixels per page

# The raw framebuffer: 128×64 => 1024 bytes
oled_buffer = bytearray(OLED_WIDTH * OLED_PAGES)

# Minimal 5×8 font for ASCII 32..126
FONT_5X8 = (
    b"\x00\x00\x00\x00\x00"  # ' '
    b"\x00\x00\x5F\x00\x00"  # '!'
    b"\x00\x07\x00\x07\x00"  # '"'
    b"\x14\x7F\x14\x7F\x14"  # '#'
    b"\x24\x2A\x7F\x2A\x12"  # '$'
    b"\x23\x13\x08\x64\x62"  # '%'
    b"\x36\x49\x55\x22\x50"  # '&'
    b"\x00\x05\x03\x00\x00"  # '''
    b"\x00\x1C\x22\x41\x00"  # '('
    b"\x00\x41\x22\x1C\x00"  # ')'
    b"\x14\x08\x3E\x08\x14"  # '*'
    b"\x08\x08\x3E\x08\x08"  # '+'
    b"\x00\x50\x30\x00\x00"  # ','
    b"\x08\x08\x08\x08\x08"  # '-'
    b"\x00\x60\x60\x00\x00"  # '.'
    b"\x20\x10\x08\x04\x02"  # '/'
    b"\x3E\x51\x49\x45\x3E"  # '0'
    b"\x00\x42\x7F\x40\x00"  # '1'
    b"\x72\x49\x49\x49\x46"  # '2'
    b"\x21\x49\x49\x49\x3E"  # '3'
    b"\x18\x14\x12\x7F\x10"  # '4'
    b"\x27\x49\x49\x49\x31"  # '5'
    b"\x3E\x49\x49\x49\x32"  # '6'
    b"\x01\x71\x09\x05\x03"  # '7'
    b"\x36\x49\x49\x49\x36"  # '8'
    b"\x26\x49\x49\x49\x3E"  # '9'
    b"\x00\x36\x36\x00\x00"  # ':'
    b"\x00\x56\x36\x00\x00"  # ';'
    b"\x08\x14\x22\x41\x00"  # '<'
    b"\x14\x14\x14\x14\x14"  # '='
    b"\x00\x41\x22\x14\x08"  # '>'
    b"\x02\x01\x59\x09\x06"  # '?'
    b"\x3E\x41\x5D\x59\x4E"  # '@'
    b"\x7C\x12\x11\x12\x7C"  # 'A'
    b"\x7F\x49\x49\x49\x36"  # 'B'
    b"\x3E\x41\x41\x41\x22"  # 'C'
    b"\x7F\x41\x41\x22\x1C"  # 'D'
    b"\x7F\x49\x49\x49\x41"  # 'E'
    b"\x7F\x09\x09\x09\x01"  # 'F'
    b"\x3E\x41\x49\x49\x7A"  # 'G'
    b"\x7F\x08\x08\x08\x7F"  # 'H'
    b"\x00\x41\x7F\x41\x00"  # 'I'
    b"\x20\x40\x41\x3F\x01"  # 'J'
    b"\x7F\x08\x14\x22\x41"  # 'K'
    b"\x7F\x40\x40\x40\x40"  # 'L'
    b"\x7F\x02\x1C\x02\x7F"  # 'M'
    b"\x7F\x04\x08\x10\x7F"  # 'N'
    b"\x3E\x41\x41\x41\x3E"  # 'O'
    b"\x7F\x09\x09\x09\x06"  # 'P'
    b"\x3E\x41\x51\x21\x5E"  # 'Q'
    b"\x7F\x09\x19\x29\x46"  # 'R'
    b"\x46\x49\x49\x49\x31"  # 'S'
    b"\x01\x01\x7F\x01\x01"  # 'T'
    b"\x3F\x40\x40\x40\x3F"  # 'U'
    b"\x1F\x20\x40\x20\x1F"  # 'V'
    b"\x7F\x20\x18\x20\x7F"  # 'W'
    b"\x63\x14\x08\x14\x63"  # 'X'
    b"\x03\x04\x78\x04\x03"  # 'Y'
    b"\x61\x51\x49\x45\x43"  # 'Z'
    b"\x00\x7F\x41\x41\x00"  # '['
    b"\x02\x04\x08\x10\x20"  # backslash
    b"\x00\x41\x41\x7F\x00"  # ']'
    b"\x04\x02\x01\x02\x04"  # '^'
    b"\x80\x80\x80\x80\x80"  # '_'
    b"\x00\x03\x05\x00\x00"  # '`'
    b"\x20\x54\x54\x54\x78"  # 'a'
    b"\x7F\x48\x44\x44\x38"  # 'b'
    b"\x38\x44\x44\x44\x20"  # 'c'
    b"\x38\x44\x44\x48\x7F"  # 'd'
    b"\x38\x54\x54\x54\x18"  # 'e'
    b"\x08\x7E\x09\x01\x02"  # 'f'
    b"\x08\x54\x54\x54\x3C"  # 'g'
    b"\x7F\x08\x04\x04\x78"  # 'h'
    b"\x00\x44\x7D\x40\x00"  # 'i'
    b"\x20\x40\x44\x3D\x00"  # 'j'
    b"\x7F\x10\x28\x44\x00"  # 'k'
    b"\x00\x41\x7F\x40\x00"  # 'l'
    b"\x7C\x04\x18\x04\x7C"  # 'm'
    b"\x7C\x08\x04\x04\x78"  # 'n'
    b"\x38\x44\x44\x44\x38"  # 'o'
    b"\x7C\x14\x14\x14\x08"  # 'p'
    b"\x08\x14\x14\x14\x7C"  # 'q'
    b"\x7C\x08\x04\x04\x08"  # 'r'
    b"\x48\x54\x54\x54\x20"  # 's'
    b"\x04\x3F\x44\x40\x20"  # 't'
    b"\x3C\x40\x40\x20\x7C"  # 'u'
    b"\x1C\x20\x40\x20\x1C"  # 'v'
    b"\x3C\x40\x30\x40\x3C"  # 'w'
    b"\x44\x28\x10\x28\x44"  # 'x'
    b"\x0C\x50\x50\x50\x3C"  # 'y'
    b"\x44\x64\x54\x4C\x44"  # 'z'
    b"\x00\x08\x36\x41\x00"  # '{'
    b"\x00\x00\x7F\x00\x00"  # '|'
    b"\x00\x41\x36\x08\x00"  # '}'
    b"\x08\x08\x2A\x1C\x08"  # '~'
)

def ssd1306_fill(value):
    """
    Fill the entire buffer with the given byte value.
    """
    for i in range(len(oled_buffer)):
        oled_buffer[i] = value

def set_pixel(px, py, color):
    """
    Set one pixel in 'oled_buffer' to color (1=on, 0=off).
    """
    if px < 0 or px >= OLED_WIDTH or py < 0 or py >= OLED_HEIGHT:
        return
    page = py // 8
    page_index = page * OLED_WIDTH + px
    bit_mask = 1 << (py % 8)
    if color:
        oled_buffer[page_index] |= bit_mask
    else:
        oled_buffer[page_index] &= ~bit_mask

def draw_char(x, y, ch):
    """
    Draw a 5×8 character from FONT_5X8 at (x,y).
    """
    code = ord(ch)
    if code < 32 or code > 126:
        code = 32  # fallback to space
    index = (code - 32) * 5
    char_data = FONT_5X8[index : index + 5]

    for col_offset, col_byte in enumerate(char_data):
        for row_bit in range(8):
            bit = (col_byte >> row_bit) & 1
            set_pixel(x + col_offset, y + row_bit, bit)

def draw_text(x, y, text):
    """
    Draw ASCII text horizontally. Each char = 5 wide + 1 spacing => 6 px total.
    """
    for ch in text:
        draw_char(x, y, ch)
        x += 6
