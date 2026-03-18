"""
slam.launch.py
==============
Launch file para SLAM do Unitree G1 com LiDAR Livox Mid360.

Problema identificado: o G1 nunca publica a TF odom → base_link.
O /dog_odom tem frame_id: odom e child_frame_id: robot_center mas
não gera TF. O nó odom_to_tf converte esse tópico em TF.

TF tree após este launch:
  odom → base_link          ← publicado por odom_to_tf (via /dog_odom)
   └── pelvis → ... → torso_link → mid360_link → livox_frame
                                                  (já publicado pelo robô)

Nós iniciados:
  1. odom_to_tf             — /dog_odom → TF odom→base_link
  2. pointcloud_to_laserscan — /livox/lidar → /scan
  3. slam_toolbox            — /scan → /map + TF map→odom
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

import os
from ament_index_python.packages import get_package_share_directory

PKG = "g1_slam"


def _pkg_path(*parts):
    return os.path.join(get_package_share_directory(PKG), *parts)


def generate_launch_description():

    arg_use_sim_time = DeclareLaunchArgument(
        "use_sim_time",
        default_value="false",
        description="true = rosbag com /clock, false = robô real.",
    )
    arg_slam_config = DeclareLaunchArgument(
        "slam_config",
        default_value=_pkg_path("config", "slam_toolbox.yaml"),
        description="Path para o YAML do slam_toolbox.",
    )
    arg_pc_config = DeclareLaunchArgument(
        "pc_config",
        default_value=_pkg_path("config", "pc_to_laserscan.yaml"),
        description="Path para o YAML do pointcloud_to_laserscan.",
    )

    use_sim_time = LaunchConfiguration("use_sim_time")
    slam_config  = LaunchConfiguration("slam_config")
    pc_config    = LaunchConfiguration("pc_config")

    # ── 1. odom → base_link TF ───────────────────────────────────────────────
    #
    #  O G1 não publica odom→base_link no TF tree.
    #  Convertemos /dog_odom em TF para fechar a cadeia:
    #    odom → base_link → pelvis → ... → livox_frame
    #
    odom_to_tf_node = Node(
        package="g1_slam",
        executable="odom_to_tf.py",
        name="odom_to_tf",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
    )

    # ── 2. PointCloud2 → LaserScan ────────────────────────────────────────────
    pc_to_laserscan_node = Node(
        package="pointcloud_to_laserscan",
        executable="pointcloud_to_laserscan_node",
        name="pc_to_ls",
        output="screen",
        parameters=[
            pc_config,
            {"use_sim_time": use_sim_time},
        ],
        remappings=[
            ("cloud_in", "/livox/lidar"),
            ("scan",     "/scan"),
        ],
    )

    # ── 3. slam_toolbox ───────────────────────────────────────────────────────
    slam_node = Node(
        package="slam_toolbox",
        executable="sync_slam_toolbox_node",
        name="slam_toolbox",
        output="screen",
        parameters=[
            slam_config,
            {"use_sim_time": use_sim_time},
        ],
    )

    return LaunchDescription([
        arg_use_sim_time,
        arg_slam_config,
        arg_pc_config,
        odom_to_tf_node,
        pc_to_laserscan_node,
        slam_node,
    ])