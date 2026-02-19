from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. Nó para converter Odometry em TF (odom -> robot_center)
        # O 'executable' deve ser igual ao que está na esquerda do '=' no setup.py
        Node(
            package='g1_slam',
            executable='odom_to_tf',
            name='odom_to_tf_broadcaster'
        ),

        Node(
            package='pointcloud_to_laserscan',
            executable='pointcloud_to_laserscan_node',
            name='pointcloud_to_laserscan',
            remappings=[
                ('cloud_in', '/livox/lidar'),
                ('scan', '/scan')
            ],
            parameters=[{
                'target_frame': 'livox_frame', # Mantém o scan no frame do sensor
                'transform_tolerance': 0.01,
                'min_height': -0.1, # Altura mínima em relação ao sensor (ajuste conforme necessário)
                'max_height': 0.1,  # Altura máxima para considerar obstáculos
                'angle_min': -3.1415, # -180 graus
                'angle_max': 3.1415,  # 180 graus
                'angle_increment': 0.0087, # Resolução (aprox 0.5 grau)
                'range_min': 0.1,
                'range_max': 30.0,
                'use_inf': True
            }]
        ),

        # 2. Transformação Estática (robot_center -> livox_frame)
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 'robot_center', 'livox_frame']
        )
    ])