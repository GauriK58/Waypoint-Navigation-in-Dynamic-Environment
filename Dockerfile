FROM osrf/ros:humble-desktop

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    sudo \
    locales \
    git \
    curl \
    wget \
    nano \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    bash-completion \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-turtlebot3 \
    ros-humble-turtlebot3-msgs \
    ros-humble-turtlebot3-simulations \
		ros-humble-turtlebot3-navigation2 \
		ros-humble-turtlebot3-teleop \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-slam-toolbox \
    && rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8

# create non root user
ARG USERNAME=ros
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} \
    && usermod -aG sudo,dialout ${USERNAME} \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}

# source env and setup turtlebot variables
RUN echo "source /opt/ros/humble/setup.bash" >> /etc/bash.bashrc \
    && echo "export TURTLEBOT3_MODEL=waffle" >> /etc/bash.bashrc \
    && echo "export GAZEBO_MODEL_PATH=\$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models" >> /etc/bash.bashrc

WORKDIR /home/${USERNAME}/ws
RUN mkdir -p src && chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}
USER ${USERNAME}

CMD ["bash"]
