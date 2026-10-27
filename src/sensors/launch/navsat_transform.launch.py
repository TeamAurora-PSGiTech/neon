from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os


def generate_launch_description():
    default_params = os.path.expanduser("~/IRC26/src/config/navsat.yaml")
    params_file = LaunchConfiguration("params_file")

    return LaunchDescription([
        DeclareLaunchArgument(
            "params_file",
            default_value=default_params,
            description="Path to navsat_transform params file",
        ),
        Node(
            package="robot_localization",
            executable="navsat_transform_node",
            name="navsat_transform",
            output="screen",
            parameters=[params_file],
            remappings=[
                ("gps/fix", "/gps"),
                ("imu", "/camera/camera/imu"),
                ("odometry/filtered", "/odometry/filtered"),
            ],
        ),
    ])
