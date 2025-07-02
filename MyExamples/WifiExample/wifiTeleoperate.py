from arduino import start, delay
from arduino_alvik import ArduinoAlvik
import network, socket, time

alvik = ArduinoAlvik()

# ----------------------------------------------------------------------
# Wi-Fi and TCP settings
# ----------------------------------------------------------------------
WIFI_SSID     = "Controllab_223"
WIFI_PASSWORD = "Controllab"
TCP_PORT      = 5050

# ----------------------------------------------------------------------
# Globals
# ----------------------------------------------------------------------
server_socket = None
client_conn   = None
current_speed = 20
speed_map     = {'2':20, '3':30, '4':40, '5':50}

# ----------------------------------------------------------------------
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi…")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(0.5)
    print("Wi-Fi connected:", wlan.ifconfig())

def start_server(port):
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)
    server_socket.settimeout(0)
    print(f"TCP listening on port {port}")

def accept_client():
    global server_socket, client_conn
    if server_socket and client_conn is None:
        try:
            conn, addr = server_socket.accept()
            print("Client connected from", addr)
            conn.settimeout(0)
            client_conn = conn
        except OSError:
            pass

def recv_commands():
    """Read incoming bytes, ignore CR/LF, and act on them."""
    global client_conn, current_speed
    if not client_conn:
        return
    try:
        data = client_conn.recv(16)
        if not data:
            print("Client disconnected")
            client_conn.close()
            client_conn = None
            return
        for b in data:
            c = chr(b)
            if c in ('\r', '\n'):
                continue

            # Speed-set
            if c in speed_map:
                current_speed = speed_map[c]
                client_conn.sendall(f"SPEED={current_speed}\r\n".encode())
                print(f"> speed set to {current_speed} RPM")

            # Motion
            elif c == 'w':
                alvik.set_wheels_speed(current_speed, current_speed)
                client_conn.sendall(b"MOVE FORWARD\r\n")
            elif c == 's':
                alvik.set_wheels_speed(-current_speed, -current_speed)
                client_conn.sendall(b"MOVE BACKWARD\r\n")
            elif c == 'd':
                alvik.set_wheels_speed(current_speed, -current_speed)
                client_conn.sendall(b"ROTATE RIGHT\r\n")
            elif c == 'a':
                alvik.set_wheels_speed(-current_speed, current_speed)
                client_conn.sendall(b"ROTATE LEFT\r\n")

            # LEDs
            elif c == '1':
                alvik.left_led.set_color(0,1,0)
                alvik.right_led.set_color(0,1,0)
                client_conn.sendall(b"LED ON\r\n")
            elif c == '0':
                alvik.left_led.set_color(0,0,0)
                alvik.right_led.set_color(0,0,0)
                client_conn.sendall(b"LED OFF\r\n")

            else:
                alvik.set_wheels_speed(0, 0)
                client_conn.sendall(f"UNK {c}\r\n".encode())

    except OSError:
        pass

def send_imu():
    """Sample IMU and send one line over TCP."""
    global client_conn
    ax, ay, az = alvik.get_accelerations()
    gx, gy, gz = alvik.get_gyros()
    line = f"IMU,{ax:.2f},{ay:.2f},{az:.2f},{gx:.2f},{gy:.2f},{gz:.2f}\r\n"
    print(line.strip())

    if client_conn:
        try:
            client_conn.sendall(line.encode())
        except OSError:
            print("Send failed; closing client")
            client_conn.close()
            client_conn = None

def setup():
    print("=== Alvik IMU+LED+Motion Wi-Fi starting up ===")
    connect_wifi(WIFI_SSID, WIFI_PASSWORD)
    start_server(TCP_PORT)
    alvik.begin()
    delay(500)
    alvik.left_led.set_color(0,1,0)
    alvik.right_led.set_color(0,1,0)

def loop():
    accept_client()
    recv_commands()
    send_imu()
    delay(100)

def cleanup():
    print("Cleaning up…")
    if client_conn:
        client_conn.close()
    if server_socket:
        server_socket.close()
    alvik.stop()

start(setup, loop, cleanup)
