docker run -d \
  --name g1_slam \
  --net=host \
  --ipc=host \
  -e ROS_DOMAIN_ID=0 \
  g1_slam:humble \
  bash -c "source /opt/ros/humble/setup.sh && source /opt/ws/install/setup.bash && ros2 launch g1_slam slam.launch.py"