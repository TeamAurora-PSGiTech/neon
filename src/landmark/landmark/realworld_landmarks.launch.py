from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():
    return LaunchDescription([

        ExecuteProcess(
            cmd=['ros2', 'launch', 'realsense2_camera', 'rs_launch.py'],
            output='screen'
        ),

        ExecuteProcess(
            cmd=['ros2', 'launch', 'rtabmap_launch', 'rtabmap.launch.py',
                 'publish_tf:=true'],
            output='screen'
        ),

        Node(
            package='landmark',
            executable='marker_publisher',
            output='screen'
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            output='screen'
        )
    ])

