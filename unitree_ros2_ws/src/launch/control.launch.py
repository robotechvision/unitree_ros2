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
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
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
    ])