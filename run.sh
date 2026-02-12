#!/usr/bin/env bash
set -e

IMAGE_NAME=g1_slam:humble

# Ajuste para o ROS_DOMAIN_ID usado no robô
ROS_DOMAIN_ID=0

docker run -it --rm \
  --name g1_slam \
  --net=host \
  --ipc=host \
  -e ROS_DOMAIN_ID=${ROS_DOMAIN_ID} \
  -e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
  ${IMAGE_NAME}