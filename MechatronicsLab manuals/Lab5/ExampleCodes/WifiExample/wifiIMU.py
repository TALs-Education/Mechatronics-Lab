from arduino import start, delay
from arduino_alvik import ArduinoAlvik
import network, socket, time

alvik = ArduinoAlvik()

# ----------------------------------------------------------------------
# Wi-Fi credentials
# ----------------------------------------------------------------------
WIFI_SSID     = "Controllab_223"
WIFI_PASSWORD = "Controllab"

# TCP Server settings
TCP_PORT      = 5050  # port to listen on

# Global variables for the TCP server
server_socket = None
client_conn   = None
client_addr   = None

# ----------------------------------------------------------------------
# Networking Setup
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
    print(f"TCP server listening on port {port}")

def accept_client():
    global server_socket, client_conn, client_addr
    if server_socket and client_conn is None:
        try:
            conn, addr = server_socket.accept()
            print("Client connected from", addr)
            conn.settimeout(0)
            client_conn, client_addr = conn, addr
        except OSError:
            pass  # no client yet

def send_to_client(msg):
    global client_conn
    if client_conn:
        try:
            client_conn.sendall(msg.encode())
        except OSError:
            print("Client disconnected.")
            client_conn.close()
            client_conn = None

# ----------------------------------------------------------------------
# Setup & Main Loop
# ----------------------------------------------------------------------
def setup():
    print("Alvik IMU-over-WiFi setup…")
    connect_wifi(WIFI_SSID, WIFI_PASSWORD)
    start_server(TCP_PORT)
    alvik.begin()
    delay(500)

def loop():
    # 1. Accept client if any
    accept_client()

    # 2. Read IMU data
    ax, ay, az = alvik.get_accelerations()
    gx, gy, gz = alvik.get_gyros()
    line = f"IMU,{ax:.2f},{ay:.2f},{az:.2f},{gx:.2f},{gy:.2f},{gz:.2f}\r\n"

    # 3. Print locally
    print(line.strip())

    # 4. Send over TCP
    send_to_client(line)

    # 5. Wait before next frame
    delay(100)

def cleanup():
    print("Cleaning up…")
    if client_conn:
        client_conn.close()
    if server_socket:
        server_socket.close()
    alvik.stop()

# Start everything
start(setup, loop, cleanup)
