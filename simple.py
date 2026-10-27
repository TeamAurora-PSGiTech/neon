import serial

# ================= SERIAL CONFIG =================
PORT = "/dev/ttyACM0"   # change to /dev/ttyUSB0 if needed
BAUD = 9600

# ================= INDEX MAP =====================
BASE = 0
ACT1 = 1
ACT2 = 2
ACT3 = 3
STEP = 4
SLD  = 5
SRD  = 6
SLA  = 7
SRA  = 8

# ================= CONSTANTS =====================
FWD  = 1
REV  = -1
STOP = 0

SAFE_STATE = [0, 0, 0, 0, 0, 1, 1, 90, 90]

# ================= SERIAL OPEN ===================
ser = serial.Serial(PORT, BAUD, timeout=1)

# Persistent robot state
u = SAFE_STATE.copy()

# ================= INSTRUCTIONS ==================
print("""
============================================================
ARM TELEOP CONTROLLER — FULL SAFETY MODE
============================================================

MOTOR CONTROLS (press key + Enter)
---------------------------------
Base Motor        : w (forward)   s (reverse)   x (stop)
Actuator 1        : e (forward)   d (reverse)   c (stop)
Actuator 2        : r (forward)   f (reverse)   v (stop)
Actuator 3        : t (forward)   g (reverse)   b (stop)
Stepper Motor     : y (forward)   h (reverse)   n (stop)

SERVO CONTROL
-------------
servo <Ldir> <Rdir> <Lang> <Rang>

Examples:
  servo 1 1 90 90
  servo 0 1 120 60

Ldir / Rdir : 1 = normal, 0 = inverted
Angles      : 0 – 180 degrees

SAFETY / EXIT
-------------
q        : 🛑 STOP ALL MOTORS (program continues)
Ctrl + C : 🛑 STOP + EXIT PROGRAM

NOTE:
- Motion is CONTINUOUS until stopped
- Empty Enter does NOTHING
============================================================
""")

# ================= SEND ==========================
def send():
    pkt = ",".join(map(str, u)) + "\n"
    ser.write(pkt.encode())
    print("TX:", u)

def stop_all():
    u[:] = SAFE_STATE
    send()
    print("🛑 ALL MOTORS STOPPED")

# ================= MAIN LOOP =====================
try:
    while True:
        line = input("> ").strip().lower()

        # Ignore empty input
        if line == "":
            continue

        # -------- STOP ONLY --------
        if line == "q":
            stop_all()
            continue

        # -------- BASE MOTOR --------
        if line == "w":   u[BASE] = FWD
        elif line == "s": u[BASE] = REV
        elif line == "x": u[BASE] = STOP

        # -------- ACTUATORS --------
        elif line == "e": u[ACT1] = FWD
        elif line == "d": u[ACT1] = REV
        elif line == "c": u[ACT1] = STOP

        elif line == "r": u[ACT2] = FWD
        elif line == "f": u[ACT2] = REV
        elif line == "v": u[ACT2] = STOP

        elif line == "t": u[ACT3] = FWD
        elif line == "g": u[ACT3] = REV
        elif line == "b": u[ACT3] = STOP

        # -------- STEPPER --------
        elif line == "y": u[STEP] = FWD
        elif line == "h": u[STEP] = REV
        elif line == "n": u[STEP] = STOP

        # -------- SERVOS --------
        elif line.startswith("servo"):
            p = line.split()
            if len(p) != 5:
                print("Usage: servo Ldir Rdir Lang Rang")
                continue
            u[SLD] = int(p[1])
            u[SRD] = int(p[2])
            u[SLA] = int(p[3])
            u[SRA] = int(p[4])

        else:
            print("Unknown command. See instructions above.")
            continue

        send()

# ================= SAFETY NET ====================
except KeyboardInterrupt:
    print("\nCtrl+C detected — exiting safely")

except Exception as e:
    print("ERROR:", e)

finally:
    print("Final safety stop...")
    stop_all()
    ser.close()
    print("CONTROLLER EXITED SAFELY")
    
