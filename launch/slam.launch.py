"""
slam.launch.py
==============
Launch file para SLAM do Unitree G1 com LiDAR Livox Mid360.

TF tree completo publicado pelo robô (não publicamos nada):
  odom → base_link → pelvis → ... → torso_link → mid360_link → livox_frame

Timestamps: /scan chega ~1.6s atrás do /tf — tolerado via transform_timeout
no slam_toolbox.yaml (transform_timeout: 2.0).

Nós iniciados:
  1. pointcloud_to_laserscan — /livox/lidar → /scan
  2. slam_toolbox            — /scan → /map + TF map→odom
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

    # ── 1. PointCloud2 → LaserScan ────────────────────────────────────────────
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

    # ── 2. slam_toolbox ───────────────────────────────────────────────────────
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
        pc_to_laserscan_node,
        slam_node,
    ])