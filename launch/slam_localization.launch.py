import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Definição de caminhos
    pkg_share = get_package_share_directory('g1_slam')
    
    # Arquivos de configuração
    map_yaml_file = '/home/mendes/Documents/mapa_g1_final.yaml'
    ekf_config_path = os.path.join(pkg_share, 'config', 'ekf.yaml')
    slam_config_path = os.path.join(pkg_share, 'config', 'localization_params.yaml')
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'localization.rviz')
    
    return LaunchDescription([
        # 1. Map Server - O dono do tópico /map
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{
                'yaml_filename': map_yaml_file, 
                'use_sim_time': True
            }]
        ),

        # 2. Lifecycle Manager - Ativa o Map Server
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_map',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'autostart': True,
                'node_names': ['map_server']
            }]
        ),

        # 3. EKF - Fusão de Sensores
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[
                ekf_config_path, 
                {'use_sim_time': True}
            ]
        ),

        # 4. TF Estática PELVIS to LIVOX_FRAME
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_pelvis_livox',
            arguments=['--x', '0', '--y', '0', '--z', '0', '--yaw', '0', '--pitch', '0', '--roll', '0', '--frame-id', 'pelvis', '--child-frame-id', 'livox_frame'],
            parameters=[{'use_sim_time': True}]
        ),

        # 5. PointCloud to LaserScan
        Node(
            package='pointcloud_to_laserscan',
            executable='pointcloud_to_laserscan_node',
            name='pointcloud_to_laserscan',
            remappings=[
                ('cloud_in', '/livox/lidar'), 
                ('scan', '/scan')
            ],
            parameters=[{
                'target_frame': 'livox_frame',
                'use_sim_time': True,
                'reliability': 'best_effort',
                'angle_increment': 0.0174
            }]
        ),

        # 6. SLAM Toolbox (Localização Pura)
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[
                slam_config_path,
                {'use_sim_time': True}
            ]
        ),

        # 7. RViz2 - Interface Visual
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_path],
            parameters=[{'use_sim_time': True}]
        )
    ])