# Manual Teleoperation via ROS 2 (No RealSense / Headless SSH)

This guide explains how to drive the rover manually over an SSH connection without launching RealSense, RTAB-Map, or Nav2.

---

## 1. Prerequisites on Rover
Ensure your user is in the `dialout` group to access the STM32 serial port without sudo:
```bash
sudo usermod -a -G dialout $USER
```
Source your workspace in every terminal:
```bash
source /opt/ros/humble/setup.bash
source ~/IRC26/install/setup.bash
```

---

## Mode A: Drive with Laptop Keyboard (over SSH)
*(No extra hardware controllers required)*

### Terminal 1 (Rover SSH): Start Motor Bridge
```bash
ros2 run motor_ctrl interface
```
*Note: If your STM32 enumerates on a different port (e.g. `/dev/ttyUSB0`), pass:*
```bash
ros2 run motor_ctrl interface --ros-args -p port:=/dev/ttyUSB0
```

### Terminal 2 (Rover SSH): Start Keyboard Teleop
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
* **Controls**:
  * `i`: Forward
  * `,`: Reverse
  * `j`: Turn Left
  * `l`: Turn Right
  * `k`: Stop
  * `q` / `z`: Increase / decrease speed by 10%

---

## Mode B: Drive with Gamepad / Joystick

### Case 1: Gamepad plugged directly into the Rover
1. **Terminal 1 (Rover SSH)**:
   ```bash
   ros2 run motor_ctrl interface
   ```
2. **Terminal 2 (Rover SSH)**:
   ```bash
   ros2 launch joystick_teleop joystick_teleop.launch.py
   ```
   *(To use a specific joystick device, e.g. `js1`: `ros2 launch joystick_teleop joystick_teleop.launch.py joy_dev:=/dev/input/js1`)*

### Case 2: Gamepad plugged into your Laptop (Remote over Wi-Fi)
Ensure both your laptop and the rover are on the same Wi-Fi network and have the same ROS domain:
```bash
export ROS_DOMAIN_ID=0
```
1. **On your Laptop**:
   ```bash
   ros2 launch joystick_teleop joystick_teleop.launch.py
   ```
2. **On the Rover (via SSH)**:
   ```bash
   ros2 run motor_ctrl interface
   ```
   *The rover automatically receives `/cmd_vel` over the network.*

---

## Joystick Controls (Default)
* **Deadman switch**: Hold **Button 0** (`A` on Xbox / `Cross` on PlayStation) to drive. Releasing immediately stops the motors.
* **Left Stick (Vertical)**: Forward / Backward.
* **Left Stick (Horizontal)**: Left / Right rotation.
* **D-Pad Up / Down**: Increase / Decrease linear speed scale.
* **D-Pad Right / Left**: Increase / Decrease angular speed scale.

