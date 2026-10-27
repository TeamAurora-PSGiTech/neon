# DOCUMENTATION

## System Requirements

* Ubuntu 20.04 or Ubuntu 22.04
* ROS 2 Humble
* Intel RealSense depth camera
* realsense2_camera ROS 2 package
* OpenCV (python3-opencv)
* cv_bridge

## Workspace Structure

The ROS 2 workspace must follow the structure below:

```
ros2_ws/
├── src/
│   └── panorama_pkg/
│       ├── panorama_pkg/
│       │   └── panorama_node.py
│       ├── setup.py
│       └── package.xml
```

## Number of Terminals Required

Three terminals are recommended for normal operation:

* **Terminal 1:** Camera driver (RealSense)
* **Terminal 2:** Panorama stitching node
* **Terminal 3:** Subscriber and visualization (base station)

## Terminal Commands

### Terminal 1 – Start the RealSense camera driver:

```bash
ros2 launch realsense2_camera rs_launch.py \
  enable_depth:=true \
  enable_imu:=true \
  align_depth:=true
```

### Terminal 2 – Build the workspace and run the panorama node:

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 run panorama_pkg panorama_node
```

### Terminal 3 – Subscribe to the stitched panorama image:

```bash
ros2 run rqt_image_view rqt_image_view
```

Select the topic:

```
/panorama/image
```

## How to Use the System

1. Focus the live camera window opened by the panorama node.
2. Rotate the camera or rover approximately **20–30 degrees** between captures.
3. Press the key **`s`** to capture each frame.
4. Capture at least **two frames** (recommended: **3–4 frames**).
5. Press the key **`q`** to stitch the panorama and publish it.
6. View the stitched panorama in **rqt_image_view** on the base station.

## Output Files Generated

All output files are saved in the following directory:

```
~/panorama_output/
```

The directory contains:

* Individual captured frames (`frame_01.jpg`, `frame_02.jpg`, etc.)
* Final stitched panorama image (`panorama_final.jpg`)

## Parameters Embedded in the Stitched Panorama

The stitched panorama image contains the following embedded information:

* Cardinal direction scale (N, E, S, W)
* Camera yaw orientation
* GPS latitude and longitude of each capture site
* Elevation (altitude)
* GPS accuracy range
* Depth-based real-world scale (minimum, mean, and maximum depth)
* Timestamp of panorama creation
* Stratigraphic layer annotations

## System Overview

This system allows the stitched panorama image to be published as a ROS 2 topic and subscribed to from a remote base station, making it suitable for rover-based exploration and monitoring applications.
