import re
import time
import requests
import serial

# ====== CONFIG ======
SERIAL_PORT = "/dev/cu.usbserial-10"  # <-- change to your port
BAUD_RATE = 115200

INFLUX_URL = "http://localhost:8086/write"
INFLUX_DB = "air_mouse"

# =====================

def write_to_influx(line_protocol: str):
    """Send a single line-protocol point to InfluxDB v1."""
    try:
        params = {"db": INFLUX_DB}
        resp = requests.post(INFLUX_URL, params=params, data=line_protocol.encode("utf-8"), timeout=2)
        print(f"[Influx] HTTP {resp.status_code}  line='{line_protocol}'")
    except Exception as e:
        print(f"[Influx ERROR] {e}  line='{line_protocol}'")


def parse_and_send(line: str):
    line = line.strip()
    if not line:
        return

    # Example: "Motion -> dx: 0.195 , dy: 0.226"
    if line.startswith("Motion -> dx:"):
        # Try to extract dx and dy as floats
        m = re.search(r"dx:\s*([-\d\.]+)\s*,\s*dy:\s*([-\d\.]+)", line)
        if m:
            dx = float(m.group(1))
            dy = float(m.group(2))
            lp = f"motion,device=esp32 dx={dx},dy={dy}"
            write_to_influx(lp)
        else:
            print(f"[PARSE MOTION FAILED] {line}")
        return

    # Example: "Right click"
    if line.startswith("Right click"):
        lp = "click,button=right value=1i"
        write_to_influx(lp)
        return

    # Example: "Left click"
    if line.startswith("Left click"):
        lp = "click,button=left value=1i"
        write_to_influx(lp)
        return

    # Anything else – just print it for debugging
    print(f"[SERIAL] {line}")


def main():
    print(f"Opening serial port {SERIAL_PORT} at {BAUD_RATE} baud...")
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("Connected. Reading lines...\n")

    # Give ESP32 a moment after reset
    time.sleep(2)

    while True:
        try:
            raw = ser.readline()
            if not raw:
                continue

            try:
                line = raw.decode("utf-8", errors="ignore")
            except Exception as e:
                print(f"[DECODE ERROR] {e} raw={raw!r}")
                continue

            parse_and_send(line)

        except KeyboardInterrupt:
            print("\nStopped by user.")
            break
        except Exception as e:
            print(f"[LOOP ERROR] {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
