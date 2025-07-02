#!/usr/bin/env python3

import socket
import threading
import time

def read_lines_in_background(sock, stop_event):
    """
    Continuously read from the socket in a background thread.
    Accumulate data in a buffer and split on newline characters.
    """
    buffer = b""
    while not stop_event.is_set():
        try:
            # Try reading some bytes (non-blocking or with a short timeout).
            data = sock.recv(1024)
            if not data:
                print("Connection closed by the Arduino.")
                stop_event.set()
                break
            
            # Append to the buffer
            buffer += data
            
            # Split on newline; handle each complete line
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                # Remove any trailing carriage returns/spaces
                line = line.replace(b"\r", b"").strip()
                if line:
                    print("Received [BG]:", line.decode("utf-8"))

        except socket.timeout:
            # If you set a timeout and no data arrives, we just loop again
            pass
        except OSError as e:
            # Socket closed or error
            print("Socket error:", e)
            stop_event.set()
            break


def main():
    # 1) Define your Arduino Nano ESP32's IP/Port
    arduino_ip = "192.168.0.101"  # <-- Replace with your device's IP
    arduino_port = 5050            # <-- Must match the TCP_PORT in your Arduino code

    # 2) Create and configure the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Optional: set a short timeout so 'recv' won't block forever
    s.settimeout(2.0)

    # 3) Attempt to connect
    try:
        s.connect((arduino_ip, arduino_port))
        print(f"Connected to Arduino Nano ESP32 at {arduino_ip}:{arduino_port}")
    except Exception as e:
        print("Failed to connect:", e)
        return

    # 4) Start a background thread to read incoming data
    stop_event = threading.Event()
    listener_thread = threading.Thread(
        target=read_lines_in_background,
        args=(s, stop_event),
        daemon=True
    )
    listener_thread.start()

    # 5) Example toggling loop:
    #    Send "1\r\n" to turn the LED on, then "0\r\n" to turn it off.
    num_toggles = 10
    for i in range(num_toggles):
        # Turn LEDs on (green)
        s.sendall(b"1\r\n")
        print("Sent: 1 (LED ON)")
        time.sleep(2)

        # Turn LEDs off
        s.sendall(b"0\r\n")
        print("Sent: 0 (LED OFF)")
        time.sleep(2)

    # 6) Cleanup: signal the background thread to stop, then close the socket
    stop_event.set()
    listener_thread.join()
    s.close()
    print("Connection closed.")


if __name__ == "__main__":
    main()
