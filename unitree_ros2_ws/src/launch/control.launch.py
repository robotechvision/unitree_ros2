#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import Command, LaunchConfiguration, EnvironmentVariable, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
# from rtv_launch.no_shared_memory_group import NoSharedMemoryGroupAction

import xacro
import yaml

def load_yaml(package_path, file_path):
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, "r") as file:
            return yaml.safe_load(file)
    except EnvironmentError:
        return None

def load_xacro(package_path, file_path):
    xacro_file = os.path.join(package_path, file_path)
    return xacro.process_file(xacro_file).toxml()

def load_file(package_path, file_path):
    absolute_file_path = os.path.join(package_path, file_path)
    with open(absolute_file_path, "r") as file:
        return file.read()

def generate_launch_description():
    pkg_share = get_package_share_directory('unitree_ros2')
    use_sim_time = LaunchConfiguration('use_sim_time')
    simulation = LaunchConfiguration('simulation')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'),

        DeclareLaunchArgument(
            'simulation',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'),

        Node(
            package='rtv_unitree_lowlevel',
            executable='joint_command_to_lowcmd_conversion',
            name='joint_command_to_lowcmd_conversion',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'simulation': simulation,
                }]
        ),

        Node(
            package='rtv_deeplab_detection',
            executable='object_detection_torch',
            name='object_detection',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'use_cpu': simulation,  # our graphic cards are not powerful enough to run GPU inference alongside simulation
                }],
            remappings=[('/camera/image_raw/compressed', '/camera/d435/color/image_raw/compressed')]
        ),

        Node(
            package='rtv_object_detection',
            executable='object_3d_info_assignment',
            name='object_3d_info_assignment',
            output='screen',
            parameters=[[pkg_share, os.path.sep, 'params', os.path.sep,
                         PythonExpression(['"simulation.yaml" if "', simulation, '".lower() == "true" else "realworld.yaml"'])], {
                'use_sim_time': use_sim_time,
            }],
        ),

        # debug
        Node(
            package='rtv_object_detection',
            executable='project_point_cloud_on_image',
            name='project_point_cloud_on_image',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'leaf_size': 0.08,
                'input_image_transport': 'raw',
            }],
            remappings=[('image', '/camera/d435/color/image_raw'),
                        ('image/compressed', '/camera/d435/color/image_raw/compressed'),
                        ('camera_info', '/camera/d435/color/camera_info'),
                        ('point_cloud', '/camera/d435/depth/color/points')],
            # prefix=["gdb -ex run --args"]
        ),

        # Node(
        #     package='rtv_image_proc',
        #     executable='image_compression',
        #     name='image_compression',
        #     output='screen',
        #     parameters=[{
        #         'use_sim_time': use_sim_time,
        #     }],
        #     remappings=[
        #         ('input', '/camera/d435/color/image_raw_noncompressed'),
        #         ('output', '/camera/d435/color/image_raw'),
        #         ('output/compressed', '/camera/d435/color/image_raw/compressed')
        #     ]
        # ),
    ])