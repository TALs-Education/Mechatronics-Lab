from arduino import *
from arduino_alvik import ArduinoAlvik

import network
import socket
import time

alvik = ArduinoAlvik()

# ----------------------------------------------------------------------
# Wi-Fi credentials
# ----------------------------------------------------------------------
WIFI_SSID = "Controllab_223"
WIFI_PASSWORD = "Controllab"

# TCP Server settings
TCP_PORT = 5050  # TCP port

# Global variables for the TCP server
server_socket = None
client_conn   = None
client_addr   = None

# ----------------------------------------------------------------------
# Networking & Alvik Setup Functions
# ----------------------------------------------------------------------

def connect_wifi(ssid, password):
    """Connect to the specified Wi-Fi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print("Already connected to Wi-Fi:", wlan.ifconfig())
        return
    
    print("Connecting to Wi-Fi...")
    wlan.connect(ssid, password)
    
    while not wlan.isconnected():
        time.sleep(0.5)
    
    print("Connected!")
    print("Network config:", wlan.ifconfig())


def start_server(port):
    """Start a TCP server listening on the specified port (non-blocking)."""
    global server_socket
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)
    server_socket.settimeout(0)  # non-blocking

    print("TCP server started on port", port)
    print("Waiting for client to connect...")


def accept_client():
    """
    Accept a new client connection if available, in non-blocking mode.
    Once accepted, set the client socket to non-blocking as well.
    """
    global server_socket, client_conn, client_addr

    if server_socket is None:
        return

    if client_conn is None:
        try:
            new_conn, new_addr = server_socket.accept()
            print("Client connected from", new_addr)
            new_conn.settimeout(0)  # non-blocking client
            client_conn, client_addr = new_conn, new_addr
        except OSError:
            # No incoming connection yet
            pass


def send_to_client(message):
    """Send a string message to the connected client (non-blocking)."""
    global client_conn
    
    if client_conn:
        try:
            client_conn.sendall(message.encode('utf-8'))
        except OSError:
            # Client disconnected or error; reset connection
            print("Client disconnected during send.")
            close_client()

# ----------------------------------------------------------------------
# Timer-Based Receive Function
# ----------------------------------------------------------------------

def receive_from_client(*args):
    """
    Attempt to read data from the connected client (non-blocking) in a timer callback.
    If data is received, pass it to parse_message().
    """
    global client_conn

    if not client_conn:
        return  # no client, nothing to read

    try:
        data = client_conn.recv(1024)  # read up to 1024 bytes
        if data:
            # Convert data from bytes to string for easier handling
            received_str = data.decode('utf-8', 'ignore').strip()
            print("Received from client:", received_str)
            
            # Parse the message in a separate function
            parse_message(received_str)
        else:
            # If `data` is empty, the client closed the connection
            print("Client disconnected.")
            close_client()
    except OSError:
        # No data available or client not connected anymore (non-blocking)
        pass


def parse_message(msg):
    """
    Handle commands sent from the client.
    - "1" → turn LEDs green
    - "0" → turn LEDs off
    - otherwise → unrecognized
    """
    if msg == "1":
        alvik.left_led.set_color(0, 1, 0)
        alvik.right_led.set_color(0, 1, 0)
        send_to_client("LED turned ON (green)\r\n")
    elif msg == "0":
        alvik.left_led.set_color(0, 0, 0)
        alvik.right_led.set_color(0, 0, 0)
        send_to_client("LED turned OFF\r\n")
    else:
        # Echo the received data as unrecognized
        send_to_client("Unrecognized input: " + msg + "\r\n")


def close_client():
    """Close the current client connection."""
    global client_conn
    if client_conn:
        try:
            client_conn.close()
        except OSError:
            pass
        client_conn = None
        print("Client socket closed.")


# ----------------------------------------------------------------------
# Setup & Main Loop
# ----------------------------------------------------------------------

def setup():
    """Called once at the beginning."""
    print("Alvik robot setup...")

    # 1. Connect to Wi-Fi
    connect_wifi(WIFI_SSID, WIFI_PASSWORD)

    # 2. Start TCP server (non-blocking)
    start_server(TCP_PORT)

    # 3. Schedule the 'receive_from_client' to be called every 500 ms
    alvik.set_timer('periodic', 500, receive_from_client, ())
    print("Scheduled receive_from_client() to run every 500 ms.")
  
    # 4. Initialize Alvik platform
    alvik.begin()
    time.sleep(1)

    # 5. Turn on LEDs green on setup
    alvik.left_led.set_color(0, 1, 0)
    alvik.right_led.set_color(0, 1, 0)




def loop():
    """Main loop called repeatedly."""
    # 1. Accept a new client if available
    accept_client()
    
    # 2. (Optional) Send a periodic greeting to the client
    send_to_client("Hello from Alvik Robot!\r\n")

    # 3. Wait 2 second so we don't spam too heavily
    delay(2000)


def cleanup():
    """Called once when the program stops."""
    print("Cleaning up...")
    alvik.stop()
    
    # Close client connection if open
    close_client()
    
    # Close server socket if open
    if server_socket:
        try:
            server_socket.close()
        except OSError:
            pass
        print("Server socket closed.")


# Start the program
start(setup, loop, cleanup)
