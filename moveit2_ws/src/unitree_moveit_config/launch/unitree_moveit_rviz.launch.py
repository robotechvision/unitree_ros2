import os
import xacro  # type: ignore

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from pathlib import Path
    
def load_xacro(package_path, file_path):
    xacro_file = os.path.join(package_path, file_path)
    return xacro.process_file(xacro_file).toxml()

def load_file(package_path, file_path):
    absolute_file_path = os.path.join(package_path, file_path)
    with open(absolute_file_path, "r") as file:
        return file.read()

def generate_launch_description():
    shared_pkg = get_package_share_directory("unitree_moveit_config")
    configs_path = os.path.join(shared_pkg, "config")
    robot_description = {"robot_description": load_xacro(configs_path, "g1_29dof_rev_1_0_with_inspire_hand_FTP.urdf.xacro")}
    robot_description_semantic = {"robot_description_semantic": load_file(configs_path, "g1_29dof_rev_1_0_with_inspire_hand_FTP.srdf")}

    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'),

        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=["-d", os.path.join(configs_path, "moveit.rviz")],
            parameters=[robot_description, robot_description_semantic, {'use_sim_time': use_sim_time}],
        ),
    ])
