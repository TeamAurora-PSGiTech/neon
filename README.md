# IRC26 - ROS 2 Robotics Workspace

A ROS 2 Humble workspace for competition rovers (Indian Rover Challenge / University Rover Challenge), featuring packages for differential drive motor control, robotic arm teleoperation, autonomous navigation (Nav2 + RTAB-Map SLAM), GPS tracking, georeferenced panoramic stitching, and video streaming.

---

## 📋 Overview of Packages

| Package | Category | Description |
|---|---|---|
| **`motor_ctrl`** | Actuation | Differential drive bridge to STM32 microcontroller over serial (115200 baud, $\pm 1000$ speed scale). |
| **`joystick_teleop`** | Teleop | Gamepad driver converting `/joy` to `/cmd_vel` with deadman safety switch and dynamic speed scaling. |
| **`arm_ctrl`** | Manipulation | Keyboard teleoperation and serial hardware interface for robotic arm links, actuators, and servos. |
| **`arm_ctrl_msgs`** | Interfaces | Custom ROS 2 message definitions (`Arm.msg`) for arm joint states and end-effector tools. |
| **`sensors`** | Navigation | NMEA GNSS serial driver publishing `sensor_msgs/NavSatFix` and NavSat transform launch files. |
| **`landmark`** | Mission | Operator landmark recorder and persistent RViz marker visualization for competition waypoints. |
| **`panorama_clean`**| Vision | RealSense frame collector and OpenCV panoramic stitching with embedded GPS coordinates and JSON metadata. |
| **`ip_feed_pkg`** | Vision | RTSP video stream receiver with real-time GPS HUD overlay and screenshot capture. |
| **`autonomous`** | AI / Vision | Trained YOLO models (`best (2).pt`) and Jupyter notebooks for autonomous cone/marker detection. |
| **`Depth_Analysis`**| Vision | Jupyter notebooks for RealSense depth point-cloud analysis and obstacle detection. |
| **`motion_control`**| Kinematics | Differential drive kinematic formulas (forward, backward, radial, in-place spot turns). |
| **`arm_sim`** | Simulation | Scaffolding for robotic arm simulation. |
| **`rover_sim`** | Simulation | Scaffolding for rover chassis simulation. |
| **`config`** | Config | Central Nav2 (`nav2_params.yaml`), EKF (`ekf.yaml`), NavSat (`navsat.yaml`), and RViz configurations. |

---

## 🛠️ Prerequisites & Installation

### Requirements
* Ubuntu 22.04 LTS or Ubuntu 20.04 LTS (or Nvidia Jetson Orin / Xavier)
* ROS 2 Humble
* Python 3.10+
* `colcon` build tools

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/TeamAurora-PSGiTech/neon.git ~/IRC26
   cd ~/IRC26
   ```

2. Install ROS dependencies:
   ```bash
   rosdep install --from-paths src --ignore-src -r -y
   ```

3. Install Python dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

4. Grant serial port permissions for STM32 and GPS:
   ```bash
   sudo usermod -a -G dialout $USER
   # Re-login or run:
   newgrp dialout
   ```
   *(Optional persistent fix: copy `udev/99-irc26-serial.rules` to `/etc/udev/rules.d/`)*

5. Build the workspace:
   ```bash
   colcon build
   source install/setup.bash
   ```

---

## 🚀 Operation Modes

### 1. Manual Teleoperation via SSH (No RealSense Needed)
Drive the rover over an SSH terminal connection without camera, SLAM, or Nav2 overhead:

#### Option A: Single-Command Teleoperation
```bash
chmod +x scripts/run_teleop.sh
./scripts/run_teleop.sh /dev/ttyACM0 keyboard
```
*(Or specify `joystick` instead of `keyboard`).*

#### Option B: Laptop Keyboard over SSH (2 Terminals)
* **Terminal 1 (Rover SSH - Motor Bridge)**:
  ```bash
  ros2 run motor_ctrl interface
  ```
  *(Pass port if different: `ros2 run motor_ctrl interface --ros-args -p port:=/dev/ttyUSB0`)*

* **Terminal 2 (Rover SSH - Keyboard Teleop)**:
  ```bash
  ros2 run teleop_twist_keyboard teleop_twist_keyboard
  ```
  * `i`: Forward
  * `,`: Reverse
  * `j`: Turn Left
  * `l`: Turn Right
  * `k`: Stop
  * `q` / `z`: Increase / decrease speed scale

#### Option C: Gamepad / Joystick Teleoperation
* **Terminal 1 (Rover SSH)**:
  ```bash
  ros2 run motor_ctrl interface
  ```
* **Terminal 2 (Rover SSH)**:
  ```bash
  ros2 launch joystick_teleop joystick_teleop.launch.py
  ```
  * **Deadman switch**: Hold **Button 0** (`A` on Xbox / `✕` on PS) to drive. Releasing stops the motors.
  * **Left Stick**: Forward / Reverse / Steer.
  * **D-Pad Up / Down**: Increase / Decrease linear speed scale.
  * **D-Pad Right / Left**: Increase / Decrease angular turn rate.

---

### 2. Autonomous Navigation (RealSense + RTAB-Map SLAM + Nav2)
For full 3D visual SLAM and autonomous waypoint navigation:

#### Multi-Terminal Stack Launcher:
```bash
chmod +x scripts/run_nav2_stack.sh
./scripts/run_nav2_stack.sh
```

#### Or launch manually step-by-step:
1. **RealSense Depth Camera**:
   ```bash
   ros2 launch realsense2_camera rs_launch.py align_depth.enable:=true pointcloud.enable:=true
   ```
2. **Static Transform (Camera to Base Link)**:
   ```bash
   ros2 run tf2_ros static_transform_publisher 0.15 0.0 0.25 0 0 0 base_link camera_link
   ```
3. **RTAB-Map Visual SLAM**:
   ```bash
   ros2 launch rtabmap_launch rtabmap.launch.py \
     rgb_topic:=/camera/camera/color/image_raw \
     depth_topic:=/camera/camera/aligned_depth_to_color/image_raw \
     camera_info_topic:=/camera/camera/color/camera_info \
     frame_id:=base_link odom_frame_id:=odom publish_tf:=true visual_odometry:=true
   ```
4. **Relay Topics**:
   ```bash
   ros2 run topic_tools relay /rtabmap/map /map &
   ros2 run topic_tools relay /rtabmap/odom /odom &
   ```
5. **Motor Driver**:
   ```bash
   ros2 run motor_ctrl interface
   ```
6. **Nav2 Stack**:
   ```bash
   ros2 launch nav2_bringup navigation_launch.py use_sim_time:=false params_file:=$HOME/IRC26/src/config/nav2_params.yaml
   ```
7. **RViz2 Visualization**:
   ```bash
   rviz2 -d ~/IRC26/src/config/navigation.rviz
   ```

---

### 3. GPS Interface & Waypoint Navigation
1. **Start GPS Node**:
   ```bash
   ros2 run sensors gps_interface
   ```
2. **Launch NavSat Transform**:
   ```bash
   ros2 launch sensors navsat_transform.launch.py
   ```
3. **Send Waypoint Goal**:
   ```bash
   ros2 run sensors gps_waypoint --ros-args -p target_lat:=<LATITUDE> -p target_lon:=<LONGITUDE>
   ```

---

### 4. Standalone Non-ROS Serial Control
Direct serial control without ROS 2:
```bash
python3 rover_control.py /dev/ttyACM0 115200
```
*(Supports non-blocking WASD terminal driving over SSH without root).*

---

## ⚙️ Microcontroller Firmware (STM32)
The rover's wheel drive uses STM32 HAL C firmware (`src/motor_ctrl/motor_ctrl/interface.c`):
* **Baud Rate**: `115200`
* **PWM Generation**: TIM1 Channels 1 & 2 (`PWM_PERIOD` 4199, `PWM_MAX` 1000)
* **Direction Pins**:
  * Motor 1: `GPIOB Pin 0`
  * Motor 2: `GPIOB Pin 1`
* **Protocol**: Text CSV packet ending in newline: `speed1,speed2\n` (range: `-1000` to `+1000`).

---

## 👥 Maintainers & Team
* **Team Aurora** - PSG iTech
* **Maintainer**: sandy (sandytheadventurer@gmail.com)
