from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    description_launch = os.path.join(
        get_package_share_directory('unitree_ros2'), 'launch', 'description.launch.py')

    realsense_launch = os.path.join(
        get_package_share_directory('realsense2_camera'), 'launch', 'rs_launch.py')

    livox_launch = os.path.join(
        get_package_share_directory('livox_ros_driver2'), 'launch', 'msg_MID360_launch.py')

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(description_launch)
        ),
        
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(realsense_launch)
        ),
        
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(livox_launch)
        )
    ])
