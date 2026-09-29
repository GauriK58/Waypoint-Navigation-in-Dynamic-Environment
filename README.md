# **chips** — *can help if people starving* :)

A dynamic obstacle-avoiding waypoint navigation robot designed as a waiter for a robotics course.

## Dockerfile

The Dockerfile:

- Installs basic utilities such as `sudo`, `git`, and `nano`
- Installs required Python packages
- Installs ROS 2 packages:
  - Gazebo for simulation environments and actors
  - TurtleBot3 packages for navigation and teleoperation
  - ROS 2 Humble utilities for navigation, SLAM, etc.
- Creates a non-root user named `ros`
- Sources the ROS environment
- Configures default TurtleBot3 variables:
  - Uses `waffle` as the default robot model
  - Configures the default TurtleBot3 Gazebo model
- Sets the working directory to `~/ws`

## Docker Commands

`clearcutex` is the Docker image name and `cc` is the container name.  
These names can be changed if required.

- Build the Docker image:

  ```bash
  docker build -t clearcutex .
  ```

- Verify that the image was built:

  ```bash
  docker images | grep clearcutex
  ```

- Allow Docker applications to access the GUI. Run once per login session:

  ```bash
  xhost +local:docker
  ```

- Create and run the container with GUI support and mount `~/cc_ws` from the host to `~/ws` inside the container:

  ```bash
  docker run -it \
    --name cc \
    --net=host \
    --ipc=host \
    -e DISPLAY=$DISPLAY \
    -e QT_X11_NO_MITSHM=1 \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ~/cc_ws:/home/ros/ws \
    clearcutex
  ```

- List all containers:

  ```bash
  docker ps -a
  ```

- Start an existing container:

  ```bash
  docker start cc
  ```

- Open a terminal inside the running container:

  ```bash
  docker exec -it cc bash
  ```

- Open additional terminals in the same container when running Gazebo, SLAM, teleop, etc.:

  ```bash
  docker exec -it cc bash
  ```

- Exit the current container terminal:

  ```bash
  exit
  ```

- Stop the container:

  ```bash
  docker stop cc
  ```

## Running chips

- Launch the default TurtleBot3 Gazebo simulation:

  ```bash
  ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
  ```

- Launch the custom restaurant world:

  ```bash
  ros2 launch ~/ws/src/rest_launch.py
  ```

- Start SLAM and RViz:

  ```bash
  ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
  ```

- In another container terminal, start keyboard teleoperation:

  ```bash
  ros2 run turtlebot3_teleop teleop_keyboard
  ```

- Drive the robot around the restaurant to create the map.

- Save/export the completed map:

  ```bash
  ros2 run nav2_map_server map_saver_cli -f ~/ws/src/maps/rest_map
  ```

  This creates files such as:

  ```text
  rest_map.yaml
  rest_map.pgm
  ```

- After mapping is complete, close SLAM and teleop.

- Start Navigation2 using the saved restaurant map:

  ```bash
  ros2 launch turtlebot3_navigation2 navigation2.launch.py \
    use_sim_time:=True \
    map:=/home/ros/ws/src/maps/rest_map.yaml
  ```

- In RViz, initialise the robot's position using **2D Pose Estimate** if required.

- Run the CHIPS waypoint navigation program:

  ```bash
  python3 ~/ws/src/chips_go.py
  ```

## Typical Terminal Setup

When running the complete simulation, use separate terminals connected to the same `cc` container:

**Terminal 1 — Gazebo**

```bash
ros2 launch ~/ws/src/rest_launch.py
```

**Terminal 2 — SLAM / Navigation**

```bash
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
```

**Terminal 3 — Teleop**

```bash
ros2 run turtlebot3_teleop teleop_keyboard
```

After mapping, replace SLAM/teleop with Navigation2 and run:

```bash
python3 ~/ws/src/chips_go.py
```
