#!/usr/bin/env bash
set -e

IMAGE_NAME=g1_slam:humble

ROS_DOMAIN_ID=0
CYCLONEDDS_HOME=/lib/cyclonedds/install

docker run -it --rm \
  --name g1_slam \
  --net=host \
  --ipc=host \
  -e ROS_DOMAIN_ID=${ROS_DOMAIN_ID} \
  -e CYCLONEDDS_HOME=${CYCLONEDDS_HOME} \
  ${IMAGE_NAME}