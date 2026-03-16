#!/usr/bin/env bash

set -e

IMAGE_NAME=g1_slam:humble
ROS_DOMAIN_ID=0

docker rm -f g1_slam 2>/dev/null || true

docker run -d \
  --name g1_slam \
  --net=host \
  --ipc=host \
  -e ROS_DOMAIN_ID=${ROS_DOMAIN_ID} \
  ${IMAGE_NAME} \
  bash -c "source /opt/ros/humble/setup.bash && \
           source /opt/ws/install/setup.bash && \
           ros2 launch g1_slam slam.launch.py"