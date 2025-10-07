from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch.actions import (DeclareLaunchArgument, SetEnvironmentVariable, ExecuteProcess, IncludeLaunchDescription,
                            GroupAction, PopLaunchConfigurations, PushLaunchConfigurations, ResetLaunchConfigurations)
from launch_ros.actions import Node
import os

def generate_launch_description():
    return LaunchDescription([
        GroupAction([
            PushLaunchConfigurations(),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(get_package_share_directory('unitree_ros2'), 'launch'), '/description.launch.py']),
            ),
            PopLaunchConfigurations(),
        ]),
        
        GroupAction([
            PushLaunchConfigurations(),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(get_package_share_directory('realsense2_camera'), 'launch'), '/rs_launch.py']),
                launch_arguments={
                    'camera_namespace': 'camera',
                    'camera_name' : 'd435',
                    'rgb_camera.color_format': 'BGR8',
                }.items()
            ),
            PopLaunchConfigurations(),
        ]),
                
        GroupAction([
            PushLaunchConfigurations(),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(get_package_share_directory('livox_ros_driver2'), 'launch_ROS2'), '/msg_MID360_launch.py']),
            ),
            PopLaunchConfigurations(),
        ]),
        
        ExecuteProcess(
            cmd=['ros2', 'param', 'set', '/camera/d435', 'pointcloud__neon_.enable', 'true'],
            output='screen'
        ),
        
        ExecuteProcess(
            cmd=['ros2', 'param', 'set', '/camera/d435', 'pointcloud__neon_.point_cloud_step', '5'],
            output='screen'
        ),
    ])
