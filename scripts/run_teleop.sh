#!/usr/bin/env bash
# ==============================================================================
# IRC26 - Standalone Manual Teleoperation (No RealSense / No SLAM / No Nav2)
# ==============================================================================

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SETUP_SCRIPT="${SETUP_SCRIPT:-"$ROOT/install/setup.bash"}"

if [[ ! -f "$SETUP_SCRIPT" ]]; then
    echo "Setup script not found at $SETUP_SCRIPT" >&2
    echo "Please build the workspace first: colcon build" >&2
    exit 1
fi

source "$SETUP_SCRIPT"

PORT="${1:-/dev/ttyACM0}"
MODE="${2:-keyboard}" # "keyboard" or "joystick"

echo "=========================================================="
echo " Starting IRC26 Manual Teleoperation"
echo " Target Port : $PORT"
echo " Mode        : $MODE"
echo "=========================================================="

# Start motor bridge in background
ros2 run motor_ctrl interface --ros-args -p port:="$PORT" &
MOTOR_PID=$!

cleanup() {
    echo -e "\nStopping teleoperation..."
    kill "$MOTOR_PID" 2>/dev/null || true
    wait "$MOTOR_PID" 2>/dev/null || true
    echo "Motors stopped."
}
trap cleanup EXIT INT TERM

sleep 1

if [[ "$MODE" == "joystick" ]]; then
    echo "Launching Joystick driver and joy_twist node..."
    ros2 launch joystick_teleop joystick_teleop.launch.py
else
    echo "Starting keyboard teleop..."
    echo "Use keys: i (fwd), , (rev), j (left), l (right), k (stop)"
    ros2 run teleop_twist_keyboard teleop_twist_keyboard
fi
