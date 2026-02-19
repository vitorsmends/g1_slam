import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('g1_slam')

    # Parâmetro de tempo simulado (rosbag)
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Config do SLAM
    slam_config_path = os.path.join(pkg_share, 'config', 'mapper_params_online_async.yaml')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),

        # 1) PointCloud -> LaserScan (gera /scan bruto)
        Node(
            package='pointcloud_to_laserscan',
            executable='pointcloud_to_laserscan_node',
            name='pc_to_ls',
            output='screen',
            remappings=[
                ('cloud_in', '/livox/lidar'),
                ('scan', '/scan')
            ],
            parameters=[{
                'target_frame': 'livox_frame',
                'transform_tolerance': 0.01,
                'min_height': -1.0,
                'max_height': 1.0,
                'angle_min': -3.1415,
                'angle_max': 3.1415,
                'angle_increment': 0.0087,
                'scan_time': 0.1,
                'range_min': 0.3,
                'range_max': 50.0,
                'use_sim_time': True,
                'reliability': 'best_effort'
            }]
        ),

        # 2) Remap + correção de TF (odom->base_link) e scan (/scan -> /scan_fixed)
        Node(
            package='g1_slam',
            executable='remap',
            name='remap',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,

                # Entradas
                'in_odom': '/dog_odom',
                'in_scan': '/scan',

                # Saídas
                'out_odom': '/dog_odom_fixed',
                'out_scan': '/scan_fixed',

                # Frames canônicos
                'odom_frame': 'odom',
                'base_frame': 'base_link',
                'lidar_frame': 'lidar_link',

                # Higiene de quaternion
                'normalize_quaternion': True
            }]
        ),

        # 3) TF estática base_link -> lidar_link (extrínsecos do LiDAR)
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_lidar_tf',
            arguments=[
                # x y z roll pitch yaw (AJUSTE PARA OS EXTRÍNSECOS REAIS)
                '0.0', '0.0', '0.0', '0.0', '0.0', '0.0',
                'base_link', 'lidar_link'
            ]
        ),

        # 4) SLAM usando o scan corrigido
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[
                slam_config_path,
                {
                    'use_sim_time': use_sim_time,
                    # Garanta que o SLAM use o scan corrigido
                    'scan_topic': '/scan_fixed',
                    'odom_frame': 'odom',
                    'base_frame': 'base_link'
                }
            ]
        ),
    ])