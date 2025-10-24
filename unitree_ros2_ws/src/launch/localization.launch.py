from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch.actions import (DeclareLaunchArgument, SetEnvironmentVariable, ExecuteProcess, IncludeLaunchDescription,
                            GroupAction, PopLaunchConfigurations, PushLaunchConfigurations, ResetLaunchConfigurations)
from launch_ros.actions import Node
from rtv_launch.no_shared_memory_group import NoSharedMemoryGroupAction
from launch.substitutions import LaunchConfiguration, PythonExpression
import os

def generate_launch_description():
    pkg_share = get_package_share_directory('unitree_ros2')
    scanmatacher_pkg = get_package_share_directory('scanmatcher')
    use_sim_time = LaunchConfiguration('use_sim_time')
    ground_map_path = LaunchConfiguration('ground_map_path')

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
        
        Node(
            package='scanmatcher',
            executable='scanmatcher_node',
            name='scan_matcher',
            namespace='site',
            parameters=[
                os.path.join(pkg_share, 'params', 'site_params.yaml'), 
            ],
            remappings=[
                ('input_cloud','/ground_height/points'),
                ('gps/odom','/gps/odom'),
            ],
            output='screen',
            # prefix='gnome-terminal -- gdb -ex run --args',
        ),
        
        NoSharedMemoryGroupAction([
            Node(
                package='graph_based_slam',
                executable='graph_based_slam_node',
                parameters=[
                    os.path.join(pkg_share, 'params', 'site_params.yaml'),
                    os.path.join(scanmatacher_pkg, 'param', 'quatro_params.yaml'),
                    os.path.join(scanmatacher_pkg, 'param', 'patchwork_params.yaml'),
                    {'use_sim_time': use_sim_time},
                    {'pose_graph_path': [ground_map_path, os.path.sep, 'pose_graph.g2o']}
                ],
                output='screen',
                # prefix='gnome-terminal -- gdb -ex run --args',
            ),
        ]),
        
        Node(
            # condition=IfCondition(LaunchConfiguration('no_vineyard_test')),
            package='rtv_ground_height',
            executable='grid_interp_ground_height',
            name='ground_height_grid_interp',
            namespace='vine_or_nav',
            output='screen',
            parameters=[
                {'base_footprint_frame': 'pelvis'},        
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
            namespace='site',
            name='odom_covariance_replacer',
            output='screen',
            remappings={('input_odom', 'odom'),
                        ('output_odom', 'odom_recovarianced')},
            parameters=[{
                'use_sim_time': use_sim_time,
                'twist_covariance': 1.0e1,
                'pose_covariance': 1.0e1,
                # 'skip_initial_duration': 2.0,
            }],
        ),
        
        Node(
            package='ekf_misc',
            executable='odom_position_integrator',
            namespace='ekf_odom',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'publish_tf': True,
                'tf_child_frame': 'pelvis'
            }],
        ),
        
        Node(
            package='robot_localization',
            executable='ekf_node',
            namespace='ekf_odom',
            name='ekf_filter_node',
            output='screen',
            remappings={('odometry/filtered', 'odom_no_pos')},
            parameters=[
                os.path.join(pkg_share, 'params', 'ekf_imu_laser.yaml'), { 
                'use_sim_time': use_sim_time,
                'publish_tf': False,
                'publish_acceleration': True,
             }],
        ),
        
        # Node(
        #     package='robot_localization',
        #     executable='ekf_node',
        #     namespace='ekf_odom',
        #     name='ekf_filter_node',
        #     output='screen',
        #     remappings={('odometry/filtered', 'odom')},
        #     parameters=[
        #         os.path.join(pkg_share, 'params', 'ekf_odom_imu.yaml'), 
        #     ],
        # ),
        
        # Node(
        #     package='robot_localization',
        #     executable='ekf_node',
        #     namespace='ekf_ground',
        #     name='ekf_filter_node',
        #     output='screen',
        #     remappings={('odometry/filtered', 'odom')},
        #     parameters=[
        #         os.path.join(pkg_share, 'params', 'ekf_ground.yaml'), 
        #     ],
        # ),
        
        # Node(
        #     package='ekf_misc',
        #     executable='zero_odom_publisher',
        #     namespace='ekf_ground',
        #     name='zero_odom_publisher',
        #     output='screen',
        #     parameters=[
        #         os.path.join(pkg_share, 'params/ekf_ground.yaml'), 
        #     ],
        # ),
        
        Node(
            package='localization_misc',
            executable='unitree_to_ros2_imu',
            name='unitree_to_ros2_imu',
            output='screen'
        ),

        Node(
            package='localization_misc',
            executable='unitree_to_ros2_odom',
            name='unitree_to_ros2_odom',
            output='screen'
        ),
        
        Node(
            # condition=IfCondition(nonstop_laser_odom),
            package='rtv_lifecycle',
            executable='lifecycle_manager',
            name='lifecycle_manager_scan_matcher',
            namespace='site',
            output='screen',
            parameters=[os.path.join(pkg_share, 'params', 'site_params.yaml'), {
                'autostart': True,
                'bond_timeout': 10000.0,
                'node_names': ['scan_matcher'],
            }],
            # Not needed, the service actually gets a unique name /site/lifecycle_manager_scan_matcher/manage_nodes
            # remappings=[('site/lifecycle_manager/manage_nodes', 'scan_matcher/lifecycle_manager/manage_nodes')],
        ),
        
        Node(
            # condition=IfCondition(LaunchConfiguration('no_vineyard_test')),
            package='rtv_lifecycle',
            executable='lifecycle_manager',
            name='lifecycle_manager',
            namespace='vine_or_nav',
            output='screen',
            parameters=[{
                'use_sim_time': False,
                'autostart': True,
                'bond_timeout': 10000.0,
                'node_names': [
                    'ground_height_grid_interp'  # must be the first node in the list (visualization_switch listens to its transition)
                ]
            }],
        ),
    ])
