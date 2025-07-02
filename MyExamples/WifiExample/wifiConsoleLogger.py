#!/usr/bin/env python3
"""
wifiConsoleLogger.py - PC-side client that combines console commands,
live IMU logging, and live IMU plotting.

• Connects to Alvik TCP IMU stream.
• Logs all IMU and wheel command samples to CSV.
• Maintains a deque of the last 100 accelerometer samples.
• Live-updates an IMU accelerometer plot in a separate thread.
• Extends console REPL to send arbitrary single-character commands (e.g., w, a, s, d).
"""

import socket
import threading
import sys
import time
from collections import deque

import matplotlib.pyplot as plt

# Configuration
DEFAULT_IP    = "192.168.0.101"
DEFAULT_PORT  = 5050
MAX_SAMPLES   = 100
PLOT_INTERVAL = 0.05  # seconds
LOG_FILENAME_FMT = "imu_console_log_{timestamp}.csv"

# Globals
stop_evt    = threading.Event()
t_deque     = deque(maxlen=MAX_SAMPLES)
ax_deque    = deque(maxlen=MAX_SAMPLES)
ay_deque    = deque(maxlen=MAX_SAMPLES)
az_deque    = deque(maxlen=MAX_SAMPLES)
logfile     = None


def parse_imu_line(line: str):
    """ Parse lines starting with 'IMU,' into numeric values """
    if not line.startswith("IMU,"):
        return None
    parts = line.split(',')
    try:
        ax, ay, az = map(float, parts[1:4])
        gx, gy, gz = map(float, parts[4:7]) if len(parts) >= 7 else (0.0, 0.0, 0.0)
        return ax, ay, az, gx, gy, gz
    except ValueError:
        return None


def reader(sock, t0):
    """ Background thread that reads from socket, logs IMU and fills deques """
    global logfile
    buffer = b""
    while not stop_evt.is_set():
        try:
            data = sock.recv(1024)
            if not data:
                stop_evt.set()
                break
            buffer += data
            while b"\n" in buffer:
                raw, buffer = buffer.split(b"\n", 1)
                txt = raw.replace(b"\r", b"").strip().decode('utf-8', 'ignore')
                if not txt:
                    continue
                # Attempt to parse IMU line
                parsed = parse_imu_line(txt)
                if parsed:
                    ax, ay, az, gx, gy, gz = parsed
                    ts = time.time() - t0
                    logfile.write(f"{ts:.3f},{ax:.3f},{ay:.3f},{az:.3f},{gx:.3f},{gy:.3f},{gz:.3f},,\n")
                    logfile.flush()
                    t_deque.append(ts)
                    ax_deque.append(ax)
                    ay_deque.append(ay)
                    az_deque.append(az)
                else:
                    print("Received [BG]:", txt)
        except socket.timeout:
            continue
        except OSError:
            stop_evt.set()
            break


def plotter():
    """ Thread to plot the last MAX_SAMPLES of accelerometer data """
    plt.ion()
    fig, ax = plt.subplots()
    line_ax, = ax.plot([], [], label='ax')
    line_ay, = ax.plot([], [], label='ay')
    line_az, = ax.plot([], [], label='az')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Acceleration (g)')
    ax.set_title('Live IMU Accelerometer')
    ax.legend()
    ax.grid(True)

    def on_close(event):
        stop_evt.set()

    fig.canvas.mpl_connect('close_event', on_close)

    while not stop_evt.is_set():
        if t_deque:
            line_ax.set_data(list(t_deque), list(ax_deque))
            line_ay.set_data(list(t_deque), list(ay_deque))
            line_az.set_data(list(t_deque), list(az_deque))
            ax.relim()
            ax.autoscale_view()
            fig.canvas.draw()
            fig.canvas.flush_events()
        time.sleep(PLOT_INTERVAL)


def main():
    ip   = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IP
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT

    # Open log file
    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    fname = LOG_FILENAME_FMT.format(timestamp=timestamp)
    global logfile
    logfile = open(fname, 'w')
    logfile.write("time_s,ax,ay,az,gx,gy,gz,command,cmd_time_s\n")

    # Connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2.0)
    try:
        sock.connect((ip, port))
        sock.settimeout(0.1)
        print(f"Connected to {ip}:{port}")
    except Exception as e:
        print("Connect failed:", e)
        logfile.close()
        return

    t0 = time.time()

    # Start reader & plotter
    thr_r = threading.Thread(target=reader, args=(sock, t0), daemon=True)
    thr_p = threading.Thread(target=plotter, daemon=True)
    thr_r.start()
    thr_p.start()

    # Console loop
    try:
        print("Enter commands (single char, e.g., w,a,s,d). Type 'q' or 'quit' to exit.")
        while not stop_evt.is_set():
            cmd = input("> ").strip()
            if cmd.lower() in ("q", "quit"):
                break
            if len(cmd) == 1:
                message = (cmd + "\r\n").encode('utf-8')
                try:
                    sock.sendall(message)
                    now = time.time() - t0
                    logfile.write(f",,,,,,,{cmd},{now:.3f}\n")
                    logfile.flush()
                    print(f"Sent: {cmd}")
                except OSError as e:
                    print("Send failed:", e)
                    break
            else:
                print("Please enter a single-character command.")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")

    # Cleanup
    stop_evt.set()
    thr_r.join()
    thr_p.join()
    sock.close()
    logfile.close()
    print(f"Logged to {fname}")


if __name__ == "__main__":
    main()
