import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('g1_slam')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    pc2ls_yaml = os.path.join(pkg_share, 'config', 'pointcloud_to_laserscan.yaml')
    remap_yaml = os.path.join(pkg_share, 'config', 'remap.yaml')
    slam_config_path = os.path.join(pkg_share, 'config', 'mapper_params_online_async.yaml')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),

        Node(
            package='pointcloud_to_laserscan',
            executable='pointcloud_to_laserscan_node',
            name='pc_to_ls',
            output='screen',
            remappings=[
                ('cloud_in', '/livox/lidar'),
                ('scan', '/scan')
            ],
            parameters=[pc2ls_yaml],
        ),

        Node(
            package='g1_slam',
            executable='remap',
            name='remap',
            output='screen',
            parameters=[remap_yaml],
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_lidar_tf',
            arguments=[
                '0.0', '0.0', '0.0',
                '0.0', '0.0', '0.0',
                'base_link', 'lidar_link'
            ]
        ),

        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[slam_config_path]
        ),
    ])