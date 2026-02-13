FROM ros:humble-ros-core

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=humble

# Install system and ROS dependencies (minimal runtime for SLAM + localization)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-colcon-common-extensions \
    python3-rosdep \
    ros-humble-slam-toolbox \
    ros-humble-robot-localization \
    ros-humble-tf2-ros \
    ros-humble-pointcloud-to-laserscan \
    && rm -rf /var/lib/apt/lists/*

# Copy the whole repository into the workspace
WORKDIR /opt/ws/src
COPY . ./g1_slam

# rosdep + build
WORKDIR /opt/ws
RUN rosdep init || true && \
    rosdep update && \
    rosdep install --from-paths src --ignore-src -r -y && \
    . /opt/ros/humble/setup.sh && \
    colcon build --symlink-install

# Auto-source environments
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc && \
    echo "source /opt/ws/install/setup.bash" >> /root/.bashrc

CMD ["bash"]