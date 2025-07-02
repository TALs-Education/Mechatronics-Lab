#!/usr/bin/env python3
"""
wifiLogger_live.py  -  PC-side client with live-updating IMU plot
---------------------------------------------------------------------
• Connects to Alviks TCP IMU stream.
• Logs all IMU samples to CSV.
• Maintains a deque of the last 100 (t, ax, ay, az) samples.
• In a “plot thread,” uses matplotlibs interactive API (plt.ion())
  to update the lines every 0.05 s.
• Stops and exits cleanly when you close the plot window or type q.
"""

import socket, threading, sys, time
from collections import deque

import matplotlib.pyplot as plt

DEFAULT_IP    = "192.168.0.101"
DEFAULT_PORT  = 5050
MAX_SAMPLES   = 100
PLOT_INTERVAL = 0.05  # seconds

# -----------------------------------------------------------------------------
# Globals for inter-thread data sharing
# -----------------------------------------------------------------------------
stop_evt = threading.Event()

# Deques for the last MAX_SAMPLES
t_deque  = deque(maxlen=MAX_SAMPLES)
ax_deque = deque(maxlen=MAX_SAMPLES)
ay_deque = deque(maxlen=MAX_SAMPLES)
az_deque = deque(maxlen=MAX_SAMPLES)

# -----------------------------------------------------------------------------
# IMU parsing + logging
# -----------------------------------------------------------------------------

def parse_imu_line(line: str):
    if not line.startswith("IMU,"):
        return None
    parts = line.split(',')
    try:
        ax, ay, az = map(float, parts[1:4])
        gx, gy, gz = map(float, parts[4:7]) if len(parts) >= 7 else (0, 0, 0)
        return ax, ay, az, gx, gy, gz
    except:
        return None

def reader(sock, logfile, t0):
    buf = b""
    while not stop_evt.is_set():
        try:
            data = sock.recv(1024)
            if not data:
                stop_evt.set()
                break
            buf += data
            while b"\n" in buf:
                raw, buf = buf.split(b"\n", 1)
                txt = raw.replace(b"\r", b"").strip().decode('utf-8', 'ignore')
                if not txt:
                    continue
                parsed = parse_imu_line(txt)
                if parsed:
                    ax, ay, az, gx, gy, gz = parsed
                    ts = time.time() - t0
                    # Log CSV
                    logfile.write(f"{ts:.3f},{ax:.3f},{ay:.3f},{az:.3f},{gx:.3f},{gy:.3f},{gz:.3f}\n")
                    logfile.flush()
                    # Push into deques
                    t_deque.append(ts)
                    ax_deque.append(ax)
                    ay_deque.append(ay)
                    az_deque.append(az)
                    print(f"PARSED: ax={ax:.2f}, ay={ay:.2f}, az={az:.2f}")
        except socket.timeout:
            continue
        except OSError:
            stop_evt.set()
            break

# -----------------------------------------------------------------------------
# Plotting thread
# -----------------------------------------------------------------------------

def plotter():
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

    # When the figure is closed, set the stop event
    def on_close(event):
        stop_evt.set()
    fig.canvas.mpl_connect('close_event', on_close)

    while not stop_evt.is_set():
        if t_deque:
            line_ax.set_data(t_deque, ax_deque)
            line_ay.set_data(t_deque, ay_deque)
            line_az.set_data(t_deque, az_deque)
            ax.relim()
            ax.autoscale_view()
            fig.canvas.draw()
            fig.canvas.flush_events()
        time.sleep(PLOT_INTERVAL)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    ip   = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IP
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT

    # Prepare log file
    tstamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    fname = f"imu_log_{tstamp}.txt"
    logfile = open(fname, 'w')
    logfile.write("time_s,ax,ay,az,gx,gy,gz\n")

    # Connect to robot
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2.0)
    try:
        sock.connect((ip, port))
        print(f"Connected to {ip}:{port}")
    except Exception as e:
        print("Connect failed:", e)
        logfile.close()
        return

    t0 = time.time()

    # Start reader & plotter threads
    thr_r = threading.Thread(target=reader, args=(sock, logfile, t0), daemon=True)
    thr_p = threading.Thread(target=plotter, daemon=True)
    thr_r.start()
    thr_p.start()

    # User loop: only for typing ‘q’ to quit
    try:
        while not stop_evt.is_set():
            cmd = input("Type q (quit) > ").strip().lower()
            if cmd == 'q':
                stop_evt.set()
    finally:
        thr_r.join()
        thr_p.join()
        sock.close()
        logfile.close()
        print(f"Logged to {fname}")

if __name__ == "__main__":
    main()
