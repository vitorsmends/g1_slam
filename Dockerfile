FROM osrf/ros:humble-ros-base

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=humble
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# System + ROS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-colcon-common-extensions \
    python3-pip \
    ros-humble-slam-toolbox \
    ros-humble-robot-localization \
    ros-humble-tf2-ros \
    ros-humble-pointcloud-to-laserscan \
    ros-humble-rviz2 \
    && rm -rf /var/lib/apt/lists/*

# Workspace
WORKDIR /opt/ws/src
COPY g1_slam ./g1_slam

# rosdep + build
WORKDIR /opt/ws
RUN rosdep update && \
    rosdep install --from-paths src --ignore-src -r -y && \
    . /opt/ros/humble/setup.sh && \
    colcon build --symlink-install

# Auto-source
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc && \
    echo "source /opt/ws/install/setup.bash" >> /root/.bashrc

CMD ["bash"]