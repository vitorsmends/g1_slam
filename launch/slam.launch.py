"""
slam.launch.py
==============
Launch file for g1 humanoid robot SLAM pipeline.

Nodes started:
  1. static_transform_publisher (x2) – publishes the two artificial static TFs
                               (robot_center → base_link → livox_frame)
                               Uses individual nodes instead of robot_state_publisher
                               to avoid conflicts if a RSP is already running on
                               the robot.
  2. pointcloud_to_laserscan – converts /livox/lidar (PointCloud2) to /scan
                               (LaserScan), re-expressed in base_link
  3. slam_toolbox (async)   – builds the map and publishes map → odom

CLI arguments:
  use_sim_time  [true|false]  default: false
  slam_config   path to a custom slam_toolbox YAML (default: bundled config)
  pc_config     path to a custom pc_to_laserscan YAML (default: bundled config)

Usage:
  # Real robot
  ros2 launch g1_slam slam.launch.py

  # Gazebo / rosbag replay
  ros2 launch g1_slam slam.launch.py use_sim_time:=true
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

import os
from ament_index_python.packages import get_package_share_directory


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

PKG = "g1_slam"


def _pkg_path(*parts):
    """Return absolute path inside this package's share directory."""
    return os.path.join(get_package_share_directory(PKG), *parts)


# ──────────────────────────────────────────────────────────────────────────────
# Launch Description
# ──────────────────────────────────────────────────────────────────────────────

def generate_launch_description():

    # ── Declare arguments ────────────────────────────────────────────────────
    arg_use_sim_time = DeclareLaunchArgument(
        "use_sim_time",
        default_value="false",
        description=(
            "Use /clock topic for time (true = simulation/rosbag replay, "
            "false = real hardware)."
        ),
    )

    arg_slam_config = DeclareLaunchArgument(
        "slam_config",
        default_value=_pkg_path("config", "slam_toolbox.yaml"),
        description="Path to slam_toolbox YAML configuration file.",
    )

    arg_pc_config = DeclareLaunchArgument(
        "pc_config",
        default_value=_pkg_path("config", "pc_to_laserscan.yaml"),
        description="Path to pointcloud_to_laserscan YAML configuration file.",
    )

    # ── Convenience substitutions ────────────────────────────────────────────
    use_sim_time = LaunchConfiguration("use_sim_time")
    slam_config  = LaunchConfiguration("slam_config")
    pc_config    = LaunchConfiguration("pc_config")

    # ── 1. Static TFs — dois nós independentes, sem robot_state_publisher ────
    #
    #  Usamos static_transform_publisher diretamente para evitar conflito com
    #  qualquer robot_state_publisher já em execução no robô. Cada nó tem um
    #  nome único e publica apenas o seu par de frames, sem tocar em
    #  /robot_description nem nas TFs do URDF do robô.
    #
    #  Junta A: robot_center → base_link  (identidade — robot_center é o root)
    #  Junta B: base_link → livox_frame   (offset físico do sensor)
    #
    #  ⚠️  Ajuste xyz/rpy da junta B para o offset real do Livox no robô.

    # Junta A: robot_center → base_link (identidade)
    tf_robot_center_to_base_link = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="tf_robot_center_to_base_link",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
        arguments=[
            # x    y    z    yaw  pitch  roll
            "0.0", "0.0", "0.0", "0.0", "0.0", "0.0",
            "robot_center",   # parent frame
            "base_link",      # child frame
        ],
    )

    # Junta B: base_link → livox_frame  (offset do sensor — AJUSTE AQUI)
    tf_base_link_to_livox = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="tf_base_link_to_livox_frame",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
        arguments=[
            # x     y     z     yaw   pitch  roll
            "0.0", "0.0", "0.30", "0.0", "0.0", "0.0",
            "base_link",    # parent frame
            "livox_frame",  # child frame
        ],
    )

    # ── 2. PointCloud → LaserScan ────────────────────────────────────────────
    #
    #  • subscribes  /livox/lidar   (sensor_msgs/PointCloud2, frame livox_frame)
    #  • publishes   /scan          (sensor_msgs/LaserScan,   frame base_link)
    #
    #  The node internally calls TF to transform livox_frame → base_link before
    #  projecting.  target_frame: base_link in the YAML handles this.
    #
    pc_to_laserscan_node = Node(
        package="pointcloud_to_laserscan",
        executable="pointcloud_to_laserscan_node",
        name="pc_to_laserscan",
        output="screen",
        parameters=[
            pc_config,
            {"use_sim_time": use_sim_time},
        ],
        remappings=[
            # Input: Livox raw cloud
            ("cloud_in", "/livox/lidar"),
            # Output: 2-D scan ready for slam_toolbox
            ("scan",     "/scan"),
        ],
    )

    # ── 3. slam_toolbox – async online SLAM ──────────────────────────────────
    slam_node = Node(
        package="slam_toolbox",
        executable="async_slam_toolbox_node",
        name="slam_toolbox",
        output="screen",
        parameters=[
            slam_config,
            {"use_sim_time": use_sim_time},
        ],
    )

    # ── Assemble ─────────────────────────────────────────────────────────────
    return LaunchDescription([
        arg_use_sim_time,
        arg_slam_config,
        arg_pc_config,
        tf_robot_center_to_base_link,
        tf_base_link_to_livox,
        pc_to_laserscan_node,
        slam_node,
    ])