from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch.actions import (DeclareLaunchArgument, SetEnvironmentVariable, ExecuteProcess, IncludeLaunchDescription,
                            GroupAction, PopLaunchConfigurations, PushLaunchConfigurations, ResetLaunchConfigurations)
from launch_ros.actions import Node
from rtv_launch.no_shared_memory_group import NoSharedMemoryGroupAction
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition, UnlessCondition
import os

def generate_launch_description():
    pkg_share = get_package_share_directory('unitree_ros2')
    scanmatacher_pkg = get_package_share_directory('scanmatcher')
    ground_map_path = LaunchConfiguration('ground_map_path')
    use_sim_time = LaunchConfiguration('use_sim_time')
    laser_odom = LaunchConfiguration('laser_odom')
    imu = LaunchConfiguration('imu')
    odom = LaunchConfiguration('odom')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time', default_value='false',
            description='Use simulation (Gazebo) clock if true'),
        
        DeclareLaunchArgument(
            'ground_map', default_value='',
            description='Directory name (in /usr/local/robotechvision/ground/maps/) where ground map is located'),

        DeclareLaunchArgument(
            'ground_map_path',
            default_value=PythonExpression(['"', os.path.join('/usr', 'local', 'robotechvision', 'ground', 'maps', ''), LaunchConfiguration('ground_map'),
                                            '" if "', LaunchConfiguration('ground_map'), '" else ""']),
            description='Path to ground map directory'),
        
        DeclareLaunchArgument(
            'laser_odom',
            default_value='false',
            description='Path to twist_mux params file. ekf_odom currently not supported in combination with imu'),

        DeclareLaunchArgument(
            'imu',
            default_value='true',
            description='Use Phidgets IMU if true. ekf_odom currently not supported in combination with laser_odom'),

        DeclareLaunchArgument(
            'odom',
            default_value='true',
            description='Do not perform any ekf odometry at all if false'),
        
        Node(
            package='scanmatcher',
            executable='scanmatcher_node',
            name='scan_matcher',
            parameters=[
                {'use_sim_time': use_sim_time},
                os.path.join(pkg_share, 'params', 'site_params.yaml')
            ],
            remappings=[('input_cloud','/ground_height/points')],
            output='screen',
            # prefix='gnome-terminal -- gdb -ex run --args',
        ),
        
        NoSharedMemoryGroupAction([
            Node(
                package='graph_based_slam',
                executable='graph_based_slam_node',
                name='graph_based_slam',
                parameters=[
                    {'use_sim_time': use_sim_time},
                    os.path.join(pkg_share, 'params', 'site_params.yaml'),
                    os.path.join(scanmatacher_pkg, 'param', 'quatro_params.yaml'),
                    os.path.join(scanmatacher_pkg, 'param', 'patchwork_params.yaml'),
                    {'pose_graph_path': [ground_map_path, os.path.sep, 'pose_graph.g2o']}
                ],
                output='screen',
                # prefix='gnome-terminal -- gdb -ex run --args',
            ),
        ]),
        
        Node(
            package='rtv_ground_height',
            executable='grid_interp_ground_height',
            name='ground_height_grid_interp',
            output='screen',
            parameters=[
                os.path.join(pkg_share, 'params', 'site_params.yaml'),
                {'use_sim_time': use_sim_time},
            ],
            remappings=[
                ('points_in', '/livox/lidar'),
                ('points_out', '/ground_height/points'),
                ('debug_markers', '/ground_height/debug_markers')
            ],
        ),
        
        Node(
            package='ekf_misc',
            executable='odom_covariance_replacer',
            name='odom_covariance_replacer',
            output='screen',
            remappings={('input_odom', 'unitree/odom'),
                        ('output_odom', 'unitree/odom_recovarianced')},
            parameters=[{
                'use_sim_time': use_sim_time,
                'twist_covariance': 1.0e1,
                'pose_covariance': 1.0e1,
                # 'skip_initial_duration': 2.0,
            }],
        ),
        
        Node(
            package='ekf_misc',
            executable='imu_covariance_replacer',
            name='imu_covariance_replacer',
            output='screen',
            remappings={('input_imu', 'imu/data'),
                        ('output_imu', 'imu/data_recovarianced')},
            parameters=[{
                'use_sim_time': use_sim_time,
            }],
        ),
        
        Node(
            condition=IfCondition(odom),
            package='robot_localization',
            executable='ekf_node',
            namespace='ekf_odom',
            name='ekf_filter_node',
            output='screen',
            remappings={('odometry/filtered', 'odom')},
            parameters=[
                [pkg_share, os.path.sep, 'params', os.path.sep,
                 PythonExpression(['"ekf_odom_laser.yaml" if "', laser_odom,
                                   '".lower() == "true" else ("ekf_odom_imu.yaml" if "', imu,
                                   '".lower() == "true" else "ekf_odom.yaml")'])],
                {'use_sim_time': use_sim_time},
            ],
        ),
        
        Node(
            condition=IfCondition(imu),
            package='robot_localization',
            executable='ekf_node',
            namespace='ekf_ground',
            name='ekf_filter_node',
            output='screen',
            remappings={('odometry/filtered', 'odom')},
            parameters=[
                {'use_sim_time': use_sim_time},
                os.path.join(pkg_share, 'params', 'ekf_ground.yaml'), 
            ],
        ),
        
        Node(
            condition=IfCondition(imu),
            package='ekf_misc',
            executable='zero_odom_publisher',
            namespace='ekf_ground',
            name='zero_odom_publisher',
            output='screen',
            parameters=[
                {'use_sim_time': use_sim_time},
                os.path.join(pkg_share, 'params', 'ekf_ground.yaml'), 
            ],
        ),
        
        Node(
            package='localization_misc',
            executable='unitree_to_ros2_imu',
            name='unitree_to_ros2_imu',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}]
        ),

        Node(
            package='localization_misc',
            executable='unitree_to_ros2_odom',
            name='unitree_to_ros2_odom',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}]
        ),
        
        Node(
            package='rtv_lifecycle',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[os.path.join(pkg_share, 'params', 'site_params.yaml'), {
                'use_sim_time': use_sim_time,
                'autostart': True,
                'bond_timeout': 10000.0,
                'node_names': ['scan_matcher','graph_based_slam', 'ground_height_grid_interp'],
            }],
        ),
    ])
