# g1_slam

ROS 2 package providing a minimal SLAM bringup pipeline for the Unitree G1 robot.  
The package currently contains a single custom node for TF and topic remapping, and a launch file that composes the SLAM pipeline using external packages.

The scope of this repository is intentionally minimal and focused on:
- Correcting TF (odom → base_link) for the G1
- Remapping odometry and LaserScan topics
- Integrating LiDAR projection to 2D and SLAM Toolbox for online mapping

---

## Requirements

- ROS 2 Humble
- slam_toolbox
- pointcloud_to_laserscan
- tf2_ros
- RViz2

Install dependencies via rosdep:

```bash
sudo rosdep init || true
rosdep update
```

---

## Workspace Setup

Create a ROS 2 workspace and add this package:

```bash
mkdir -p ~/g1_ws/src
cd ~/g1_ws/src
git clone <REPOSITORY_URL>/g1_slam.git
cd ..
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
```

---

## Launch

This repository provides a single launch file that brings up the full online SLAM pipeline.

### Pipeline

1. LiDAR PointCloud → LaserScan  
   The LiDAR point cloud is projected into a 2D LaserScan using `pointcloud_to_laserscan`.

2. TF and topic remapping (custom node)  
   The `g1_slam/remap` node:
   - Subscribes to kinematic odometry (`/dog_odom`)
   - Publishes corrected odometry
   - Republishes LaserScan on a fixed topic
   - Publishes TF odom → base_link using the kinematic odometry

3. Static TF (base_link → lidar_link)  
   A static transform publisher provides the LiDAR extrinsics.

4. Online SLAM (slam_toolbox)  
   `slam_toolbox` runs in async mapping mode using the corrected LaserScan and TF chain.

### Run

```bash
ros2 launch g1_slam slam.launch.py
```

---

## Configuration

All parameters used by the pipeline are provided via YAML configuration files:

- `config/pointcloud_to_laserscan.yaml`  
  Parameters for LiDAR point cloud projection to LaserScan.

- `config/remap.yaml`  
  Parameters for the custom remap node:
  - input odometry topic
  - input scan topic
  - output odometry topic
  - output scan topic
  - frame names
  - TF publishing behavior

- `config/mapper_params_online_async.yaml`  
  Official SLAM Toolbox configuration used for online mapping.

No other launch files or configuration files are part of this repository.

---

## Topics and Frames

### Topics

| Type   | Topic           | Description                                |
|--------|------------------|--------------------------------------------|
| Input  | /livox/lidar     | LiDAR point cloud                          |
| Input  | /dog_odom        | Kinematic odometry from the robot          |
| Output | /scan            | Raw LaserScan from pointcloud_to_laserscan |
| Output | /scan_fixed      | Remapped LaserScan used by SLAM            |
| Output | /dog_odom_fixed  | Corrected odometry used for TF             |
| Output | /map             | Occupancy grid map from slam_toolbox       |

### TF Tree

The expected TF chain during operation is:

```
map → odom → base_link → lidar_link
```

---

## Visualization

```bash
rviz2
```

Recommended displays:
- TF
- Map
- LaserScan (/scan_fixed)
- Robot model (base_link)

---

## Verification

```bash
ros2 node list
ros2 topic list
ros2 node info /slam_toolbox
ros2 topic echo /scan_fixed
ros2 topic echo /map
```

---

## Known Limitations

- Localization on a prebuilt map is not provided in this repository.
- Sensor fusion (EKF) is intentionally not part of this package.
- Navigation and path planning are out of scope.
- The static TF between base_link and lidar_link must be manually calibrated.

---

## Status

Active development.  
The current implementation is focused on stabilizing TF and SLAM integration on the Unitree G1 for 2D navigation use cases.
