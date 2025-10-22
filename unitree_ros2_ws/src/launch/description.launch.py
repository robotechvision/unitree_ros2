#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import Command, LaunchConfiguration, EnvironmentVariable
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
# from rtv_launch.no_shared_memory_group import NoSharedMemoryGroupAction
import xacro  # type: ignore

def load_xacro(package_path, file_path):
    xacro_file = os.path.join(package_path, file_path)
    return xacro.process_file(xacro_file).toxml()

def generate_launch_description():
    pkg_share = get_package_share_directory('unitree_ros2')
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    robot_type = LaunchConfiguration('robot_type', default='g1')
    
    configs_path = os.path.join(get_package_share_directory("unitree_moveit_config"), "config")
    robot_desc = load_xacro(configs_path, "g1_29dof_rev_1_0_with_inspire_hand_FTP.urdf.xacro")

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'),
        DeclareLaunchArgument('robot_type',
                              default_value='g1',
                              description='What type of robot api to use'),
        DeclareLaunchArgument(
            'description_file',
            default_value='g1_29dof_rev_1_0_with_inspire_hand_FTP.urdf',
            description='Filename of robot urdf located in unitree_ros2/description/<robot_type>/'),

        # NoSharedMemoryGroupAction([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'robot_description': robot_desc,
                }]),
        # ]),
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'source_list': ['lowstate_joint_states', 'hand_joint_states'],
                'rate': 100,
            }]),
        Node(
            package='rtv_unitree_lowlevel',
            executable='lowstate_joint_state_publisher',
            name='lowstate_joint_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
            }]),
    ])