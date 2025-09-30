import os
import sys
import yaml # type: ignore
import xacro  # type: ignore

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from pathlib import Path

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
    shared_pkg = get_package_share_directory("unitree_moveit_config")
    configs_path = os.path.join(shared_pkg, "config")
    
    robot_description = {"robot_description": load_xacro(configs_path, "g1_29dof_rev_1_0_with_inspire_hand_FTP.urdf.xacro")}
    robot_description_semantic = {"robot_description_semantic": load_file(configs_path, "g1_29dof_rev_1_0_with_inspire_hand_FTP.srdf")}
    
    moveit_simple_controllers_yaml = load_yaml(configs_path, "moveit_controllers.yaml")
    moveit_controllers = {
        "moveit_simple_controller_manager": moveit_simple_controllers_yaml,
        "moveit_controller_manager": "moveit_simple_controller_manager/MoveItSimpleControllerManager",
    }
    
    joint_limits_yaml = load_yaml(configs_path, "joint_limits.yaml")
    kinematics_yaml = load_yaml(configs_path, "kinematics.yaml") 
    ros2_controllers_yaml = os.path.join(configs_path, "ros2_controllers.yaml")
    
    ompl_planning_pipeline_config = {
        "move_group": {
            "planning_plugin": "ompl_interface/OMPLPlanner",
            "request_adapters": """default_planner_request_adapters/AddTimeOptimalParameterization default_planner_request_adapters/LimitMaxCartesianLinkSpeed default_planner_request_adapters/FixWorkspaceBounds default_planner_request_adapters/FixStartStateBounds default_planner_request_adapters/FixStartStateCollision default_planner_request_adapters/FixStartStatePathConstraints stomp_moveit/StompSmoothingAdapter""",
            "start_state_max_bounds_error": 0.1,
        },
        "planning_pipelines": ["move_group"],
        "default_planning_pipeline": "move_group",
        "capabilities": "move_group/MoveGroupMoveAction move_group/ExecuteTaskSolutionCapability",
    }
    ompl_planning_yaml = load_yaml(configs_path, "ompl_planning.yaml")
    ompl_planning_pipeline_config["move_group"].update(ompl_planning_yaml)

    return LaunchDescription([
        Node(
            package='controller_manager',
            executable='ros2_control_node',
            parameters=[robot_description, ros2_controllers_yaml],
            output='screen'
        ),
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['left_arm_controller', 
                       'right_arm_controller',
                       'left_hand_controller',
                       'right_hand_controller'],
            output='screen',
        ),
        Node(
            package="moveit_ros_move_group",
            executable="move_group",
            name="move_group",
            output="screen",
            parameters=[
                robot_description,
                robot_description_semantic,
                kinematics_yaml,
                joint_limits_yaml,
                ompl_planning_pipeline_config,
                moveit_controllers,
                {"execute_start_state": False},
            ],
        ),
        # Node(
        #     package="rviz2",
        #     executable="rviz2",
        #     name="rviz2",
        #     output="screen",
        #     arguments=["-d", os.path.join(configs_path, "moveit.rviz")],
        #     parameters=[robot_description, robot_description_semantic],
        # ),
    ])
