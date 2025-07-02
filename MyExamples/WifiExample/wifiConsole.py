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
            data = sock.recv(1024)
            if not data:
                print("Connection closed by the Arduino.")
                stop_event.set()
                break

            buffer += data
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                line = line.replace(b"\r", b"").strip()
                if line:
                    print("Received [BG]:", line.decode("utf-8"))

        except socket.timeout:
            pass
        except OSError as e:
            print("Socket error:", e)
            stop_event.set()
            break

def main():
    arduino_ip   = "192.168.0.101"  # ← update as needed
    arduino_port = 5050            # ← must match your server

    # 1) Create and configure the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2.0)

    # 2) Connect
    try:
        s.connect((arduino_ip, arduino_port))
        print(f"Connected to Arduino at {arduino_ip}:{arduino_port}")
    except Exception as e:
        print("Failed to connect:", e)
        return

    # 3) Start listener thread
    stop_event = threading.Event()
    listener = threading.Thread(
        target=read_lines_in_background,
        args=(s, stop_event),
        daemon=True
    )
    listener.start()

    # 4) REPL: read from console, send to Arduino
    print("Type '1' to turn LEDs on, '0' to turn them off, or 'quit' to exit.")
    try:
        while not stop_event.is_set():
            cmd = input("> ").strip()
            if cmd.lower() in ("quit", "exit"):
                break
            # send whatever user typed, add CRLF so Arduino can parse it
            message = (cmd + "\r\n").encode('utf-8')
            try:
                s.sendall(message)
                print(f"Sent: {cmd}")
            except OSError as e:
                print("Send failed:", e)
                break
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")

    # 5) Cleanup
    stop_event.set()
    listener.join()
    s.close()
    print("Connection closed.")

if __name__ == "__main__":
    main()
