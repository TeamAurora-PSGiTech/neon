import sys
import time
import serial

# ==============================
# SERIAL CONFIGURATION
# ==============================
# Usage: python3 rover_control.py [/dev/ttyACM0] [115200]
PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
BAUD_RATE = int(sys.argv[2]) if len(sys.argv) > 2 else 115200

try:
    ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"--- Connected to STM32 on {PORT} at {BAUD_RATE} baud ---")
except serial.SerialException as e:
    print(f"ERROR: Could not open {PORT}: {e}")
    print("Pass port as argument: python3 rover_control.py /dev/ttyUSB0 (or COM8 on Windows)")
    sys.exit(1)


# ==============================
# SPEED CONFIGURATION
# ==============================
speed = 500
MIN_SPEED = 100
MAX_SPEED = 1000
SPEED_STEP = 100

movement = "stop"


# ==============================
# SEND COMMAND
# ==============================
def send_motor(left, right):
    left = max(-1000, min(1000, left))
    right = max(-1000, min(1000, right))
    command = f"{left},{right}\n"
    ser.write(command.encode("utf-8"))
    print(
        f"\rMovement: {movement:<8} Speed: {speed:<4} Command: {left:>5},{right:<5}",
        end="",
        flush=True,
    )


# ==============================
# APPLY CURRENT MOVEMENT
# ==============================
def apply_movement():
    if movement == "forward":
        send_motor(speed, speed)
    elif movement == "backward":
        send_motor(-speed, -speed)
    elif movement == "left":
        send_motor(-speed, speed)
    elif movement == "right":
        send_motor(speed, -speed)
    else:
        send_motor(0, 0)


def forward():
    global movement
    movement = "forward"
    apply_movement()


def backward():
    global movement
    movement = "backward"
    apply_movement()


def left():
    global movement
    movement = "left"
    apply_movement()


def right():
    global movement
    movement = "right"
    apply_movement()


def stop():
    global movement
    movement = "stop"
    apply_movement()


def increase_speed():
    global speed
    speed = min(MAX_SPEED, speed + SPEED_STEP)
    apply_movement()


def decrease_speed():
    global speed
    speed = max(MIN_SPEED, speed - SPEED_STEP)
    apply_movement()


# ==============================
# NON-BLOCKING KEYBOARD HELPER (SSH & CROSS-PLATFORM)
# ==============================
def get_key():
    """Reads a single keypress without requiring Enter, works over SSH."""
    if sys.platform == "win32":
        import msvcrt
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch in (b"\x00", b"\xe0"):  # Arrow keys
                code = msvcrt.getch()
                if code == b"H":
                    return "up"
                elif code == b"P":
                    return "down"
            try:
                return ch.decode("utf-8").lower()
            except UnicodeDecodeError:
                return None
        return None
    else:
        import select
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
            if rlist:
                ch = sys.stdin.read(1)
                if ch == "\x1b":  # Escape sequence for arrow keys
                    seq = sys.stdin.read(2)
                    if seq == "[A":
                        return "up"
                    elif seq == "[B":
                        return "down"
                return ch.lower()
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


# ==============================
# MAIN LOOP
# ==============================
def main():
    print("\n6-Wheel Rover Controller (SSH & Local Terminal)")
    print("-------------------------------------------------")
    print("W / w      : Forward")
    print("S / s      : Backward")
    print("A / a      : Left (turn in place)")
    print("D / d      : Right (turn in place)")
    print("+ / Up     : Increase speed (+100)")
    print("- / Down   : Decrease speed (-100)")
    print("Space / x  : STOP")
    print("Q / q      : Quit")
    print("-------------------------------------------------")

    stop()

    try:
        while True:
            key = get_key()
            if not key:
                time.sleep(0.02)
                continue

            if key in ("w", "W"):
                forward()
            elif key in ("s", "S"):
                backward()
            elif key in ("a", "A"):
                left()
            elif key in ("d", "D"):
                right()
            elif key in (" ", "x"):
                stop()
            elif key in ("+", "up"):
                increase_speed()
            elif key in ("-", "down"):
                decrease_speed()
            elif key in ("q", "\x03"):  # q or Ctrl+C
                break

    finally:
        stop()
        if ser.is_open:
            ser.close()
        print("\n\nRover safely stopped. Connection closed.")


if __name__ == "__main__":
    main()

