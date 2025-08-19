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

@expose_substitution('file-content')
class FileContent(Substitution):
    """
    Substitution that reads the contents of a file.

    If the file is not found a `SubstitutionFailure` error is raised.
    """

    def __init__(self, path: SomeSubstitutionsType) -> None:
        """Create a FileContent substitution."""
        super().__init__()

        from launch.utilities import normalize_to_list_of_substitutions
        self.__path = normalize_to_list_of_substitutions(path)

    @classmethod
    def parse(cls, data: Sequence[SomeSubstitutionsType]):
        """Parse `FileContent` substitution."""
        if not data or len(data) != 1:
            raise AttributeError('file content substitutions expect 1 argument')
        kwargs = {'path': data[0]}
        return cls, kwargs

    @property
    def path(self) -> List[Substitution]:
        """Getter for path."""
        return self.__path

    def describe(self) -> Text:
        """Return a description of this substitution as a string."""
        return 'FileContent({})'.format(
            ', '.join([sub.describe() for sub in self.path]))

    def perform(self, context: LaunchContext) -> Text:
        """Perform the substitution by evaluating the expression."""
        from launch.utilities import perform_substitutions
        path = perform_substitutions(context, self.path)
        try:
            with open(path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise SubstitutionFailure('File not found: {}'.format(path))

############################################################################################################

def generate_launch_description():
    pkg_share = get_package_share_directory('unitree_ros2')
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    robot_type = LaunchConfiguration('robot_type', default='g1')
    robot_desc = FileContent([pkg_share, '/description/', robot_type, '/', LaunchConfiguration('description_file')])

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