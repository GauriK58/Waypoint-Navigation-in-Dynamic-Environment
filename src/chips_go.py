#!/usr/bin/env python3

"""
chips's mission planner!!!

shows table to number mapping
asks for sequence
orders using greedy alg
sends waypoints to nav2
marks waypoints in rviz2
returns to kitchen

needs:
- nav2 must be running
- gazebo must be running with chips in it
- chips must be localised (use 2d pose estimate)
"""

import math

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from visualization_msgs.msg import Marker, MarkerArray


# table coords (got from publish point)
TABLES = {
    "table_1": (5.464768886566162, -3.9170689582824707, 0.0),
    "table_2": (5.95006799697876, -6.284769058227539, 0.0),
    "table_3": (5.418345928192139, -8.252248764038086, 0.0),
    "table_4": (8.912660598754883, -6.332099437713623, 0.0),
    "table_5": (8.252593994140625, -8.288040161132812, 0.0),
    "table_6": (10.732320785522461, -8.776232719421387, 0.0),
    "table_7": (15.706441879272461, -2.3784334659576416, 0.0),
    "table_8": (15.543872833251953, -9.992376327514648, 0.0),
    "table_9": (19.49358367919922, -3.1760711669921875, 0.0),
    "table_10": (19.15202522277832, -8.802520751953125, 0.0),
    "table_11": (24.812273025512695, -5.581315517425537, 0.0),
    "table_12": (28.020605087280273, -5.678124904632568, 0.0),
    "kitchen": (0.0, 0.0, 0.0),
}

HOME_POSITION = TABLES["kitchen"]


# calculate euclidean distance
def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# order waypoints using greedy nearest-neighbour
# start_pos: (x, y, t) start position
# waypoint: dictionary {name: (x, y, t)}
# returns: list (name, (x, y, t)) in order
def greedy_order(start_pos, waypoints):

    if not waypoints:
        return []

    remaining = dict(waypoints)

    # kitchen is never a waypoint
    remaining.pop("kitchen", None)

    ordered = []
    current = start_pos[:2]

    while remaining:
        nearest_name = None
        nearest_dist = float("inf")

        for name, pos in remaining.items():
            dist = euclidean_distance(current, pos[:2])
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_name = name

        ordered.append((nearest_name, remaining[nearest_name]))
        current = remaining[nearest_name][:2]
        del remaining[nearest_name]

    return ordered


# create poststamped messages fro nav22
def create_pose_stamped(navigator, x, y, yaw):

    pose = PoseStamped()
    pose.header.frame_id = "map"
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.position.z = 0.0

    # yaw -> quaternion
    pose.pose.orientation.x = 0.0
    pose.pose.orientation.y = 0.0
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)

    return pose


class WaiterMission:

    def __init__(self):
        self.navigator = BasicNavigator()

        # marker publisher for rviz2
        self.marker_pub = self.navigator.create_publisher(
            MarkerArray,
            "/waypoints",
            10
        )

        # current mission markers to keep republishing
        self.current_ordered_waypoints = []

        # republish markers periodically so rviz doesn't miss them
        self.marker_timer = self.navigator.create_timer(
            1.0,
            self.marker_timer_callback
        )

		# republish active waypoint markers every second
    def marker_timer_callback(self):
        if self.current_ordered_waypoints:
            self.publish_waypoint_markers(self.current_ordered_waypoints)

		# wait for nav2 to be active
    def wait_for_nav2(self):
        print("waiting for nav2 to become active...")
        self.navigator.waitUntilNav2Active()
        print("nav2 is active!")

		# display all tables
    def display_tables(self):
        print("\n" + "=" * 50)
        print("available tables / waypoints")
        print("=" * 50)
        for i, (name, pos) in enumerate(TABLES.items(), 1):
            print(f"  {i}. {name:12s} -> x={pos[0]:.2f}, y={pos[1]:.2f}")
        print("=" * 50)
        print("i always start from the kitchen and return to the kitchen btw :>")

		# user select tables
    def select_tables(self):
        table_names = list(TABLES.keys())

        print("\nwhat tables should i visit? (comma-separated), or 'all' for all tables:")
        print("e.g.: 1,3,4  or  all")
        print("note: kitchen is used automatically as start/end you don't have to select it.")

        while True:
            selection = input("> ").strip().lower()

            if selection == "all":
                return dict(TABLES)

            if selection in ("q", "quit"):
                return None

            try:
                indices = [int(x.strip()) for x in selection.split(",")]
                selected = {}

                for idx in indices:
                    if 1 <= idx <= len(table_names):
                        name = table_names[idx - 1]
                        selected[name] = TABLES[name]
                    else:
                        print(f"not a table :/ : {idx}")

                if selected:
                    return selected

                print("no valid tables selected :((( try again!")

            except ValueError:
                print("invalid input! enter numbers separated by commas, 'all', or 'q' to quit")

		# clear markers from rviz
    def clear_markers(self):
        marker_array = MarkerArray()

        marker = Marker()
        marker.header.frame_id = "map"
        marker.header.stamp = self.navigator.get_clock().now().to_msg()
        marker.action = Marker.DELETEALL

        marker_array.markers.append(marker)
        self.marker_pub.publish(marker_array)

		# publish markers: red spheres + offset labels
    def publish_waypoint_markers(self, ordered_waypoints):

        marker_array = MarkerArray()
        now = self.navigator.get_clock().now().to_msg()

        for idx, (name, pos) in enumerate(ordered_waypoints):
            x, y, _yaw = pos

            # red sphere
            sphere = Marker()
            sphere.header.frame_id = "map"
            sphere.header.stamp = now
            sphere.ns = "mission_points"
            sphere.id = idx
            sphere.type = Marker.SPHERE
            sphere.action = Marker.ADD
            sphere.pose.position.x = x
            sphere.pose.position.y = y
            sphere.pose.position.z = 0.15
            sphere.pose.orientation.w = 1.0
            sphere.scale.x = 0.25
            sphere.scale.y = 0.25
            sphere.scale.z = 0.25
            sphere.color.a = 1.0
            sphere.color.r = 1.0
            sphere.color.g = 0.0
            sphere.color.b = 0.0
            marker_array.markers.append(sphere)

            # white text label
            text = Marker()
            text.header.frame_id = "map"
            text.header.stamp = now
            text.ns = "mission_labels"
            text.id = 1000 + idx
            text.type = Marker.TEXT_VIEW_FACING
            text.action = Marker.ADD
            text.pose.position.x = x+0.2
            text.pose.position.y = y
            text.pose.position.z = 0.55
            text.pose.orientation.w = 1.0
            text.scale.z = 0.25
            text.color.a = 1.0
            text.color.r = 0.0
            text.color.g = 0.0
            text.color.b = 0.0
            text.text = f"{idx + 1}:{name}"
            marker_array.markers.append(text)

        self.marker_pub.publish(marker_array)

		# execute mission
    def run_mission(self, ordered_waypoints):

        if not ordered_waypoints:
            print("no tables selected to visit :(")
            return

        # store and publish markers for RViz
        self.current_ordered_waypoints = ordered_waypoints
        self.clear_markers()
        self.publish_waypoint_markers(ordered_waypoints)

        print("\n" + "-" * 50)
        print("mission plan (greedy nearest-neighbour order)")
        print("-" * 50)

        total_dist = 0.0
        prev_pos = HOME_POSITION

        print(f"  start -> kitchen      (x={HOME_POSITION[0]:.2f}, y={HOME_POSITION[1]:.2f})")

        for i, (name, pos) in enumerate(ordered_waypoints, 1):
            dist = euclidean_distance(prev_pos, pos)
            total_dist += dist
            print(f"  {i}. {name:12s} (dist from prev: {dist:.2f}m)")
            prev_pos = pos

        return_dist = euclidean_distance(prev_pos, HOME_POSITION)
        total_dist += return_dist
        print(f"  end -> kitchen       (dist from last table: {return_dist:.2f}m)")

        print(f"\ntotal estimated distance including return: {total_dist:.2f}m")
        print("=" * 50)

        confirm = input("\nshould i go? (y/n): ").strip().lower()
        if confirm != "y":
            print("aw okay not going :<")
            return

        waypoint_poses = []
        for name, pos in ordered_waypoints:
            pose = create_pose_stamped(self.navigator, pos[0], pos[1], pos[2])
            waypoint_poses.append(pose)

        print("\n>>> starting waypoint navigation...")
        self.navigator.followWaypoints(waypoint_poses)

        current_index = -1
        while not self.navigator.isTaskComplete():
            feedback = self.navigator.getFeedback()
            if feedback:
                if feedback.current_waypoint != current_index:
                    current_index = feedback.current_waypoint
                    if current_index < len(ordered_waypoints):
                        print(f">>> heading to: {ordered_waypoints[current_index][0]}")

        result = self.navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            print("\n*** all selected tables visited successfully!!! ***")
            self.return_home()
        elif result == TaskResult.CANCELED:
            print("\n*** mission was cancelled :( ***")
        elif result == TaskResult.FAILED:
            print("\n*** mission failed!!! check nav2 logs for details ***")
        else:
            print(f"\n*** mission ended with result: {result} ***")

		# nav to kitchen before start
    def go_to_kitchen(self):
        print("\n>>> going to kitchen to start mission...")

        kitchen_pose = create_pose_stamped(
            self.navigator,
            HOME_POSITION[0],
            HOME_POSITION[1],
            HOME_POSITION[2]
        )

        self.navigator.goToPose(kitchen_pose)

        while not self.navigator.isTaskComplete():
            pass

        result = self.navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            print(">>> at kitchen. i'm ready!!!")
            return True
        else:
            print(f">>> i couldn't reach kitchen :( : {result}")
            return False

		# return to kitchen
    def return_home(self):
        """Automatically return to kitchen/home position."""
        print("\n>>> returning to kitchen...")

        home_pose = create_pose_stamped(
            self.navigator,
            HOME_POSITION[0],
            HOME_POSITION[1],
            HOME_POSITION[2]
        )

        self.navigator.goToPose(home_pose)

        while not self.navigator.isTaskComplete():
            pass

        result = self.navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            print(">>> arrived back at kitchen!")
        else:
            print(f">>> i couldn't return to kitchen :( : {result}")


def main():
    print("\n" + "-" * 50)
    print("-  chips mission planner")
    print("-" * 50)

    rclpy.init()

    try:
        waiter = WaiterMission()
        waiter.wait_for_nav2()

        while True:
            waiter.display_tables()
            selected = waiter.select_tables()

            if selected is None:
                print("exiting...")
                break

            # go to kitchen first, then plan and run mission
            if not waiter.go_to_kitchen():
                print("could not reach kitchen! skipping this mission")
                continue

            current_pos = HOME_POSITION
            ordered = greedy_order(current_pos, selected)

            waiter.run_mission(ordered)

            again = input("\nwanna go again? (y/n): ").strip().lower()
            if again != "y":
                break

    except KeyboardInterrupt:
        print("\ninterrupted by user.")
    finally:
        rclpy.shutdown()

    print("bye bye!!! :>")


if __name__ == "__main__":
    main()
