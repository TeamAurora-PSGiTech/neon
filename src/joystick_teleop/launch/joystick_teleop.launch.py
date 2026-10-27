from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    joy_dev = LaunchConfiguration("joy_dev")

    return LaunchDescription([
        DeclareLaunchArgument(
            "joy_dev",
            default_value="/dev/input/js0",
            description="Path to the joystick device node",
        ),
        Node(
            package="joy",
            executable="joy_node",
            name="joy_node",
            output="screen",
            parameters=[{
                "dev": joy_dev,
                "deadzone": 0.1,
                "autorepeat_rate": 20.0,
            }],
        ),
        Node(
            package="joystick_teleop",
            executable="joy_twist",
            name="joy_twist",
            output="screen",
        ),
    ])

