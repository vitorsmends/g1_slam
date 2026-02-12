# g1_slam

ROS 2 package providing SLAM and localization bringup for the Unitree G1
robot, including mapping, localization, and state estimation (EKF).

------------------------------------------------------------------------

## Requirements

-   ROS 2 Humble
-   slam_toolbox
-   robot_localization
-   RViz2
-   TF2

Install dependencies via rosdep (recommended):

``` bash
sudo rosdep init || true
rosdep update
```

------------------------------------------------------------------------

## Workspace Setup

Create a ROS 2 workspace and add this package:

``` bash
mkdir -p ~/g1_ws/src
cd ~/g1_ws/src
git clone <REPOSITORY_URL>/g1_slam.git
cd ..
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
```

------------------------------------------------------------------------

## Launch Files

### 1) slam_simple.launch.py --- Online SLAM (Mapping)

**Purpose:**\
Runs online SLAM to build a map using slam_toolbox in mapping mode.

**Pipeline behavior:** - slam_toolbox runs in mapping mode - Consumes
LaserScan from LiDAR - Uses TF odom → base_link (pelvis) - Publishes
/map and TF map → odom

**Configuration:** - config/mapper_params.yaml - mode: mapping -
scan_topic: /scan - base_frame: pelvis - odom_frame: odom - map_frame:
map - Loop closing enabled (do_loop_closing: true) - Map resolution:
0.05 m

**Run:**

``` bash
ros2 launch g1_slam slam_simple.launch.py
```

**Expected outputs:** - /map - /tf (map → odom) - /slam_toolbox/\*

------------------------------------------------------------------------

### 2) slam_localization.launch.py --- Localization on a Prebuilt Map

**Purpose:**\
Runs localization on an existing map using slam_toolbox in localization
mode and sensor fusion with EKF (robot_localization).

**Pipeline behavior:** 1. EKF (robot_localization) estimates odom →
base_link (pelvis) 2. slam_toolbox (localization) estimates map → odom
using LiDAR 3. The full TF chain is closed: map → odom → pelvis

**Configurations:** - config/localization_params.yaml (slam_toolbox --
localization) - mode: localization - scan_topic: /scan - base_frame:
pelvis - odom_frame: odom - map_frame: map - Loop closing disabled
(do_loop_closing: false)

-   config/ekf.yaml (robot_localization -- EKF)

    **Odometry sensors:**

    -   /dog_odom
    -   /dog_imu_raw

    **Frames:**

    -   map_frame: map
    -   odom_frame: odom
    -   base_link_frame: pelvis
    -   world_frame: odom

**Run:**

``` bash
ros2 launch g1_slam slam_localization.launch.py
```

**Expected outputs:** - /map - /tf (map → odom, odom → pelvis) -
/odometry/filtered - /slam_toolbox/\*

------------------------------------------------------------------------

## Sensors and Estimation Pipeline

### Odometry Estimation (EKF)

**Inputs:**

  Sensor           Topic          Usage
  ---------------- -------------- -----------------------------
  Robot odometry   /dog_odom      Planar pose and orientation
  IMU              /dog_imu_raw   Yaw and angular velocity

**Node:** - robot_localization (EKF)

**Outputs:** - TF: odom → pelvis - /odometry/filtered

------------------------------------------------------------------------

### Mapping and Localization (SLAM Toolbox)

**Inputs:**

  Sensor   Topic   Usage
  -------- ------- ------------------------
  LiDAR    /scan   Scan matching for SLAM

**Node:** - slam_toolbox

**Modes:** - Mapping: builds the map (slam_simple.launch.py) -
Localization: localizes on a prebuilt map (slam_localization.launch.py)

------------------------------------------------------------------------

## Visualization (RViz)

Use the provided RViz configuration:

``` bash
rviz2 -d config/localization.rviz
```

Includes: - Map - TF - LiDAR scans - Estimated pose

------------------------------------------------------------------------

## Testing

``` bash
colcon test
```

------------------------------------------------------------------------

## Important Notes

-   Robot base frame: pelvis

-   SLAM consumes LaserScan on /scan

-   EKF consumes only /dog_odom and /dog_imu_raw

-   The map is published on /map

-   Expected TF chain:

        map → odom → pelvis

------------------------------------------------------------------------

## Recommended Next Steps

-   Document map saving and loading (slam_toolbox save_map)
-   Add a launch file for localization with a loaded map
-   Add rosbag recording instructions
-   Add mandatory topic checks

------------------------------------------------------------------------

## License

TBD

------------------------------------------------------------------------

## Contributing

TBD

------------------------------------------------------------------------

## Status

Under active development.
