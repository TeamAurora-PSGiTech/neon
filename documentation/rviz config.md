# Full Run — RealSense → RTAB-Map → Nav2 → RViz → Goal

This document contains the **working command flow** using terminal commands only.

---

## 1. Start the RealSense camera

```bash
ros2 launch realsense2_camera rs_launch.py \
  align_depth.enable:=true \
  pointcloud.enable:=true


(Keep this terminal running)

2. Start RTAB-Map (Visual SLAM / Localization)
ros2 launch rtabmap_launch rtabmap.launch.py \
  rgb_topic:=/camera/camera/color/image_raw \
  depth_topic:=/camera/camera/aligned_depth_to_color/image_raw \
  camera_info_topic:=/camera/camera/color/camera_info \
  frame_id:=base_link \
  odom_frame_id:=odom \
  map_frame_id:=map \
  publish_tf:=true \
  visual_odometry:=true \
  approx_sync:=true \
  rtabmap_viz:=false \
  delete_db_on_start:=true


(Keep this terminal running)

3. (Optional) Relay RTAB-Map topics to standard names
ros2 run topic_tools relay /rtabmap/map /map
ros2 run topic_tools relay /rtabmap/odom /odom


(Only needed if other nodes expect /map and /odom)

4. Publish camera → base_link static TF
ros2 run tf2_ros static_transform_publisher \
  0.15 0.0 0.25 \
  0 0 0 \
  base_link camera_link


(Keep this terminal running)

5. Launch Nav2
ros2 launch nav2_bringup navigation_launch.py \
  use_sim_time:=false \
  autostart:=true


(Wait ~10 seconds)

6. Launch RViz with saved config
rviz2 -d ~/IRC26/src/config/navigation.rviz

7. Send navigation goal (terminal)
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{ \
  pose: { header: { frame_id: 'map' }, \
  pose: { position: { x: 2.0, y: 1.0, z: 0.0 }, \
  orientation: { w: 1.0 } } } }"

Command Order Summary
ros2 launch realsense2_camera rs_launch.py
ros2 launch rtabmap_launch rtabmap.launch.py
ros2 run tf2_ros static_transform_publisher ...
ros2 launch nav2_bringup navigation_launch.py
rviz2 -d ~/IRC26/src/config/navigation.rviz
ros2 action send_goal /navigate_to_pose ...
