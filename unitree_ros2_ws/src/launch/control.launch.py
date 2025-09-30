#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import Command, LaunchConfiguration, EnvironmentVariable, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
# from rtv_launch.no_shared_memory_group import NoSharedMemoryGroupAction

############################################################################################################
##### FileContent substitution not present in Humble, so we define it here (TODO: find a better place) #####
############################################################################################################

from typing import List
from typing import Sequence
from typing import Text

from launch.substitutions.substitution_failure import SubstitutionFailure
from launch.frontend import expose_substitution
from launch.launch_context import LaunchContext
from launch.some_substitutions_type import SomeSubstitutionsType
from launch.substitution import Substitution

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
            remappings=[
                ('/camera/camera/depth/color/points', '/camera/d435/depth/color/points'),
                ('camera_info', '/camera/d435/color/camera_info'),
            ],
        ),

        # # debug
        # Node(
        #     package='rtv_object_detection',
        #     executable='project_point_cloud_on_image',
        #     name='project_point_cloud_on_image',
        #     output='screen',
        #     parameters=[{
        #         'use_sim_time': use_sim_time,
        #         'leaf_size': 0.08,
        #     }],
        #     remappings=[('image/compressed', '/realsense/color/image_raw/compressed'),
        #                 ('point_cloud', '/stereo_points')],
        # ),

        Node(
            package='rtv_image_proc',
            executable='image_compression',
            name='image_compression',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
            }],
            remappings=[
                ('input', '/camera/d435/color/image_raw_noncompressed'),
                ('output', '/camera/d435/color/image_raw'),
                ('output/compressed', '/camera/d435/color/image_raw/compressed')
            ]
        ),
    ])