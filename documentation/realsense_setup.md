# **Prerequisites**

### **Install ROS 2 (Humble recommended)**

Follow the official [ROS 2 installation instructions](https://index.ros.org/doc/ros2/Installation/).

### **Install Intel RealSense SDK and ROS 2 Wrapper**

1.  Switch to the root user:
    
    ```bash
    sudo passwd root
    su root
    ```
    
2.  Update and upgrade your system:
    
    ```bash
    apt-get update && apt-get upgrade && apt-get dist-upgrade
    ```
    
3.  Install required dependencies:
    
    ```bash
    apt-get install libssl-dev libusb-1.0-0-dev libudev-dev pkg-config libgtk-3-dev
    apt-get install git wget cmake build-essential
    apt-get install libglfw3-dev libgl1-mesa-dev libglu1-mesa-dev
    ```
    
4.  Clone the RealSense repository:
    
    ```bash
    git clone https://github.com/realsenseai/librealsense.git
    ```

5. Run Realsense permissions script from _librealsense2_ root directory:
   ```sh
   cd librealsense
   ./scripts/setup_udev_rules.sh
   ```
   Notice: You can always remove permissions by running: `./scripts/setup_udev_rules.sh --uninstall`

6. Build and apply patched kernel modules for:
    * Ubuntu 20/22/24 (focal/jammy/noble) with LTS kernel 5.15, 5.19, 6.5, 6.8, 6.11, 6.14 \
      `./scripts/patch-realsense-ubuntu-lts-hwe.sh`
    * Ubuntu 20 with LTS kernel (< 5.13) \
     `./scripts/patch-realsense-ubuntu-lts.sh`
    
6.  Build and install the RealSense SDK:
    
    ```bash
    cd librealsense
    mkdir build && cd build
    cmake ../ -DBUILD_EXAMPLES=true
    make uninstall && make clean && make && make install
    ```
    
7.  Verify the RealSense setup by running the viewer:
    
    ```bash
    realsense-viewer
    ```
    

> **Note:** For Jetson devices, follow the instructions at [jetson-orin-librealsense](https://github.com/jetsonhacks/jetson-orin-librealsense).