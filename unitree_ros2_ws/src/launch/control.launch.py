#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import Command, LaunchConfiguration, EnvironmentVariable
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
            executable='object_detection',
            name='object_detection',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'use_cpu': simulation,  # our graphic cards are not powerful enough to run GPU inference alongside simulation
                }],
            remappings=[('/camera/image_raw/compressed', '/realsense/color/image_raw/compressed')]
        ),

        Node(
            package='rtv_image_proc',
            executable='image_compression',
            name='image_compression',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
            }],
            remappings=[
                ('input', '/realsense/color/image_raw_noncompressed'),
                ('output', '/realsense/color/image_raw'),
                ('output/compressed', '/realsense/color/image_raw/compressed')
            ]
        ),
    ])