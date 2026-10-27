📍 Landmark Setup — Recording & Visualizing Map Landmarks (IRC26)

This document explains how to record, store, and visualize landmarks on a SLAM-generated map using the IRC26 Landmark System.

A landmark is a manually operator-defined point of interest, recorded at the rover’s current pose in the map frame, and stored persistently for reuse across system restarts.

This system is intentionally simple, deterministic, and competition-safe.

🔧 Prerequisites

Before running the landmark system, ensure:

ROS 2 Humble is installed and sourced

Workspace ~/IRC26 builds without errors

Intel RealSense camera is connected and detected

RTAB-Map is publishing a valid map

Nav2 is running successfully

A valid TF tree exists:

map → odom → base_link


Verify with:

ros2 topic echo /tf

🚀 Full Run — Landmark System (Terminal-wise)

🔹 TERMINAL 1 — Start Intel RealSense Camera

source /opt/ros/humble/setup.bash

ros2 launch realsense2_camera rs_launch.py \
  align_depth.enable:=true \
  pointcloud.enable:=true


📌 Purpose

Starts RGB + depth streams

Provides input for RTAB-Map SLAM

⚠️ Keep this terminal running.

🔹 TERMINAL 2 — Start RTAB-Map (Visual SLAM)

source /opt/ros/humble/setup.bash

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
  delete_db_on_start:=true


📌 Purpose

Generates SLAM map

Publishes /map, /odom, and TF transforms

⚠️ Keep this terminal running.

🔹 TERMINAL 3 — Publish Static TF (Camera → Base Link)

source /opt/ros/humble/setup.bash

ros2 run tf2_ros static_transform_publisher \
  0 0 0 \
  0 0 0 \
  base_link camera_link


📌 Purpose

Fixes camera frame alignment

Required for correct SLAM and localization

🔹 TERMINAL 4 — Relay Map Topic

source /opt/ros/humble/setup.bash

ros2 run topic_tools relay /rtabmap/map /map


📌 Purpose

Makes RTAB-Map map available as /map

Required by Nav2 and RViz

🔹 TERMINAL 5 — Relay Odometry Topic

source /opt/ros/humble/setup.bash

ros2 run topic_tools relay /rtabmap/odom /odom


📌 Purpose

Standardizes odometry topic for Nav2

🔹 TERMINAL 6 — Start Nav2

source /opt/ros/humble/setup.bash

ros2 launch nav2_bringup navigation_launch.py \
  use_sim_time:=false


📌 Purpose

Enables localization and navigation

Provides stable map → odom → base_link tracking

⏱️ Wait ~10 seconds for full initialization.

🔹 TERMINAL 7 — Landmark Recorder (Keyboard Input)

cd ~/IRC26
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash

ros2 run landmark landmark_recorder


You should see:

Press keys to save landmarks:

🎮 Keyboard Controls
Key	Landmark Color
l	Red
a	Light Blue
s	Orange
d	Brown
f	Pink
g	Yellow
h	Purple
j	Dark Blue
k	Dark Green
;	Cyan

📌 What happens on key press

Current robot pose is read from the map frame

A new landmark is appended to a YAML file

Marker is published immediately for RViz

Landmark ID increments automatically

🔹 TERMINAL 8 — Marker Publisher (Persistent Visualization)

cd ~/IRC26
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash

ros2 run landmark marker_publisher


📌 Purpose

Reloads landmarks from disk

Republishes markers periodically

Ensures markers persist after restart

🔹 TERMINAL 9 — RViz

source /opt/ros/humble/setup.bash
rviz2

RViz Configuration Checklist

Fixed Frame: map

Add Displays:

Map

TF

Marker (/landmark_markers)

RobotModel (optional)

📂 Landmark Storage

All landmarks are stored persistently at:

~/IRC26/src/landmark/config/landmarks.yaml


To view:

cat ~/IRC26/src/landmark/config/landmarks.yaml

Stored Data Includes

id (unique, auto-incremented)

x, y coordinates (meters)

color_name

RGB color values

📌 Frame reference: map
📌 Persistence: survives restart

📝 Design Notes (Honest Engineering)

Landmarks are manual, operator-defined

No orientation or semantic labels are stored

No automatic feature extraction

Color is used only for human interpretation

System prioritizes reliability over automation

✅ Summary

Using this setup, operators can:

Manually mark important locations on a SLAM map

Assign visual categories using color

Persist landmarks across reboots

Instantly visualize all landmarks in RViz

This landmark system is simple, robust, and competition-appropriate, with no hidden assumptions.
