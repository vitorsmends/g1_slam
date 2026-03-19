docker run -d \
  --name g1_slam \
  --restart unless-stopped \
  --net=host \
  --ipc=host \
  -e ROS_DOMAIN_ID=${ROS_DOMAIN_ID} \
  -v ~/g1_slam:/opt/ws \
  ${IMAGE_NAME} \
  bash -c "source /opt/ros/humble/setup.bash && cd /opt/ws && colcon build && source install/setup.bash && ros2 launch g1_slam slam.launch.py"