**chips**: can help if people starving

a dynamic obstacle avoiding waypoint navigator robot
waiter for a robotics course

everything hosted on repo at https://git.sr.ht/~adisawi/chips

Dockerfile
- installs basic stuff (`sudo`, `git`, `nano`, etc)
- installs `python3` stuff
- installs ros2 stuff
	- `gazebo` for the environment + actors
	- `turtlebot3` for the bot (with navigation, teleop, etc)
	- general utilities from `humble` (navigation, slam, etc)
- creates non-root user `ros`
- sources env
- sets up default turtlebot vars
	- `waffle` for model (can be changed later)
	- default turtlebot gazebo model for env
- working directory is `~/ws`

### commands
`[name]` is `clearcutex` or `cc`, can be changed when running
- with dockerfile in directory, build
	```
docker build -t clearcutex .
	```
- verify build
	```
docker images | grep clearcutex
	```
- allow gui (run once per login session) (linux only i think)
	```
xhost +local:docker
	```
- run container (with display stuff + link to `~/cc_ws` outside) (linux only i think)
	```
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
- list all containers
	```
docker ps -a
	```
- start container
	```
docker start cc
	```
- open another terminal in same container
	```
docker exec -it cc bash
	```
- stop containter
	```
exit
docker stop cc
	```

actually relevant stuff
- launch default turtlebot gazebo sim
	```
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
	```
- launch custom restaurant world
	```
ros2 launch ~/ws/src/rest_launch.py
	```
- start slam and show rviz
	```
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
	```
- run teleop (in another container) to control with wasd
	```
ros2 run turtlebot3_teleop teleop_keyboard
	```
- export map (assuming directory exists)
	```
ros2 run nav2_map_server map_saver_cli -f ~/ws/src/maps/rest_map
	```
- (after closing slam and teleop) start nav
	```
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
  use_sim_time:=True \
  map:=/home/ros/ws/src/maps/rest_map.yaml
	```
	might have to initialise 2D pose
- run navigation
	```
python3 ~/ws/src/chips_go.py
	```
