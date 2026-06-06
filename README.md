# g1_slam

<p align="center">
  <video src="assets/g1-slam.mp4" controls width="100%"></video>
</p>

> SLAM, localization and navigation for the Unitree G1 humanoid robot using ROS 2, Livox Mid360, SLAM Toolbox and Nav2.

![ROS2 Humble](https://img.shields.io/badge/ROS2-Humble-blue)
![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-orange)
![Nav2](https://img.shields.io/badge/Nav2-Supported-success)
![SLAM Toolbox](https://img.shields.io/badge/SLAM-Toolbox-success)

The package provides a lightweight navigation stack tailored for the Unitree G1, including:

- PointCloud2 → LaserScan conversion
- Timestamp synchronization for odometry and LiDAR streams
- TF generation (`odom → base_link`)
- SLAM Toolbox mapping
- SLAM Toolbox localization
- Nav2 integration
- RViz visualization

---

## 1. Overview

### 1.1 Architecture

```text
Livox PointCloud2
        │
        ▼
restamp_cloud
        │
        ▼
pointcloud_to_laserscan
        │
        ▼
/scan
        │
        ▼
slam_toolbox
        │
        ▼
map
```

```text
/dog_odom
      │
      ▼
restamp_odom
      │
      ▼
odom_to_tf
      │
      ▼
odom → base_link
```

```text
slam_toolbox
      │
      ▼
map → odom
      │
      ▼
pose_publisher
      │
      ▼
/inorbit/odom_pose
      │
      ▼
Nav2
```

### 1.2 Package Structure

```text
g1_slam/
├── config/
│   ├── nav2_params.yaml
│   ├── pc_to_laserscan.yaml
│   ├── slam_toolbox.yaml
│   └── slam_toolbox_localize.yaml
├── launch/
│   ├── nav.launch.py
│   ├── rviz.launch.py
│   └── slam.launch.py
├── g1_slam/
│   ├── odom_to_tf.py
│   ├── pose_publisher.py
│   ├── restamp_cloud.py
│   └── restamp_odom.py
├── Dockerfile
├── build.sh
└── run.sh
```

---

## 2. Installation

### 2.1 Docker (Recommended)

Build the image:

```bash
./build.sh
```

Run the container:

```bash
./run.sh
```

Open a shell inside the running container:

```bash
docker exec -it g1_slam bash
```

### 2.2 Native Installation

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

git clone <REPOSITORY_URL>/g1_slam.git

cd ..

rosdep install --from-paths src --ignore-src -r -y

colcon build --packages-select g1_slam --symlink-install

source install/setup.bash
```

---

## 3. Operation

### 3.1 Mapping

Build a new map from scratch.

```bash
ros2 launch g1_slam slam.launch.py
```

### 3.2 Localization

Load an existing map and estimate the robot pose without modifying it.

```bash
ros2 launch g1_slam slam.launch.py \
  slam_config:=<path_to>/slam_toolbox_localize.yaml
```

### 3.3 Navigation

Start the Nav2 stack.

```bash
ros2 launch g1_slam nav.launch.py
```

Features:

- Global path planning
- Local obstacle avoidance
- Goal-based navigation
- Velocity smoothing
- Costmap generation from LiDAR data

### 3.4 RViz

```bash
ros2 launch g1_slam rviz.launch.py
```

---

## 4. Maps

### 4.1 Save Occupancy Map

```bash
ros2 run nav2_map_server map_saver_cli \
-f ~/maps/map
```

### 4.2 Save Posegraph

```bash
ros2 service call /slam_toolbox/serialize_map \
slam_toolbox/srv/SerializePoseGraph \
"{filename: '/home/unitree/maps/map_robotspace'}"
```

---

## 5. Interfaces

### 5.1 Topics

| Direction | Topic | Description |
|------------|--------|-------------|
| Input | `/livox/lidar` | Raw Livox point cloud |
| Input | `/dog_odom` | Robot odometry |
| Output | `/scan` | 2D LaserScan |
| Output | `/map` | Occupancy map |
| Output | `/inorbit/odom_pose` | Robot pose in map frame |
| Output | `/cmd_vel` | Navigation commands |

### 5.2 TF Tree

```text
map
 └── odom
      └── base_link
           └── ...
                └── livox_frame
```

---

## 6. Verification

```bash
ros2 node list

ros2 topic hz /scan

ros2 topic hz /map

ros2 topic hz /inorbit/odom_pose

ros2 run tf2_ros tf2_echo odom base_link

ros2 run tf2_ros tf2_echo map odom
```

---

## 7. Notes

### 7.1 Custom Nodes

**restamp_odom.py**  
Synchronizes odometry timestamps with the ROS clock.

**restamp_cloud.py**  
Synchronizes Livox point clouds before SLAM processing.

**odom_to_tf.py**  
Publishes the `odom → base_link` transform from robot odometry.

**pose_publisher.py**  
Publishes the robot pose in the map frame as a standard `Odometry` message.

### 7.2 Known Limitations

- Sensor fusion is not included.
- Map quality depends on odometry quality.
- Localization mode requires a previously serialized posegraph.
- LiDAR extrinsics must be correctly configured on the robot.

---

## Status

Active development.
