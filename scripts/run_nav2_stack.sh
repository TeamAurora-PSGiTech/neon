#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Configurable options
: "${USE_SIM_TIME:=false}"
: "${INTERFACE_MODE:=auto}"   # auto | const
: "${SETUP_SCRIPT:="$ROOT/install/setup.bash"}"
: "${SEND_TEST_GOAL:=false}"
: "${GOAL_X:=2.0}"
: "${GOAL_Y:=1.0}"

if [[ ! -f "$SETUP_SCRIPT" ]]; then
  echo "Setup script not found at $SETUP_SCRIPT" >&2
  echo "Set SETUP_SCRIPT to your ROS 2 setup file." >&2
  exit 1
fi

if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
  echo "No graphical session detected. Open a GUI session or use tmux manually." >&2
  exit 1
fi

launch_terminal() {
  local title="$1"
  local cmd="$2"

  if command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal --title="$title" -- bash -lc "set -e; $cmd; exec bash"
  elif command -v konsole >/dev/null 2>&1; then
    konsole --new-tab -p tabtitle="$title" -e bash -lc "set -e; $cmd; exec bash"
  elif command -v xterm >/dev/null 2>&1; then
    xterm -T "$title" -e bash -lc "set -e; $cmd; exec bash" &
  else
    echo "No supported terminal emulator found (gnome-terminal, konsole, xterm)." >&2
    exit 1
  fi
}

COMMON_PREFIX="source \"$SETUP_SCRIPT\""

REALSENSE_CMD="$COMMON_PREFIX; \
ros2 launch realsense2_camera rs_launch.py \
  align_depth.enable:=true \
  pointcloud.enable:=true \
  enable_gyro:=true \
  enable_accel:=true \
  unite_imu_method:=1"

STATIC_TF_CMD="$COMMON_PREFIX; \
ros2 run tf2_ros static_transform_publisher \
  0.15 0.0 0.25 \
  0 0 0 \
  base_link camera_link"

RTABMAP_CMD="$COMMON_PREFIX; \
ros2 launch rtabmap_launch rtabmap.launch.py \
  rgb_topic:=/camera/camera/color/image_raw \
  depth_topic:=/camera/camera/aligned_depth_to_color/image_raw \
  camera_info_topic:=/camera/camera/color/camera_info \
  frame_id:=base_link \
  odom_frame_id:=odom \
  publish_tf:=true \
  visual_odometry:=true \
  approx_sync:=true \
  rtabmap_viz:=false \
  delete_db_on_start:=true"

RELAY_MAP_CMD="$COMMON_PREFIX; ros2 run topic_tools relay /rtabmap/map /map"
RELAY_ODOM_CMD="$COMMON_PREFIX; ros2 run topic_tools relay /rtabmap/odom /odom"

if [[ "$INTERFACE_MODE" == "const" ]]; then
  MOTOR_CMD="$COMMON_PREFIX; ros2 run motor_ctrl const"
else
  MOTOR_CMD="$COMMON_PREFIX; ros2 run motor_ctrl interface"
fi

NAV2_CMD="$COMMON_PREFIX; \
ros2 launch nav2_bringup navigation_launch.py \
  use_sim_time:=$USE_SIM_TIME \
  params_file:=$ROOT/src/config/nav2_params.yaml"

GOAL_CMD="$COMMON_PREFIX; \
for i in {1..60}; do \
  if ros2 action list | grep -q '/navigate_to_pose'; then break; fi; \
  sleep 1; \
done; \
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \"{ pose: { header: { frame_id: 'map' }, pose: { position: { x: $GOAL_X, y: $GOAL_Y, z: 0.0 }, orientation: { z: 0.0, w: 1.0 } } } }\""

launch_terminal "RealSense" "$REALSENSE_CMD"
launch_terminal "Static TF" "$STATIC_TF_CMD"
launch_terminal "RTAB-Map" "$RTABMAP_CMD"
launch_terminal "Relay /map" "$RELAY_MAP_CMD"
launch_terminal "Relay /odom" "$RELAY_ODOM_CMD"
launch_terminal "Motor Ctrl" "$MOTOR_CMD"
launch_terminal "Nav2" "$NAV2_CMD"

if [[ "$SEND_TEST_GOAL" == "true" ]]; then
  launch_terminal "Nav2 Test Goal" "$GOAL_CMD"
fi

echo "Launched all commands in separate terminals."
