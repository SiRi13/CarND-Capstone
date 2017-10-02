#!/usr/bin/env python

import rospy
import tf
import math

def get_closest_waypoint(waypoints, pose):
    """Identifies the closest path waypoint to the given position
        https://en.wikipedia.org/wiki/Closest_pair_of_points_problem
    Args:
        pose (Pose): position to match a waypoint to

    Returns:
        int: index of the closest waypoint in self.waypoints

    """
    # TODO implement
    return 0


def get_next(base_pose, pose_list):
    """
    Returns index of the next list entry to base_pose
    :param base_pose: Single Pose (e.g. current pose)
    :param pose_list: List with poses to search for the closest
    :return: Index of closest list entry and distance
    """
    closest_dist = float("inf")
    closest_index = 0

    for i in range(0, len(pose_list)):
        # Check if pose in list in in front of the vehicle
        if check_is_ahead(base_pose.pose, pose_list[i].pose.pose):

            # Calculate the distance between pose und pose in list
            dist = squared_dist(base_pose, pose_list[i].pose)

            # If distance is smaller than last saved distance
            if dist < closest_dist:
                # Save
                closest_dist = dist
                closest_index = i
    return closest_index, math.sqrt(closest_dist)


def get_closest_stop_line(tl_pose, tl_list):
    """
    Finds the closest stop line to the traffic light
    :param tl_pose: pose of traffic light
    :param tl_list: pose of stop line according to tl_pose
    :return: index of list entry
    """
    closest_dist = float("inf")
    closest_index = 0

    for i in range(0, len(tl_list)):
        # Check if ahead (probably not necessary

        # Calculate the distance between tl_pose and poses in list
        dx = tl_pose.position.x - tl_list[i][0]
        dy = tl_pose.position.y - tl_list[i][1]
        dist = dx * dx + dy * dy

        if dist < closest_dist:
            # Save
            closest_dist = dist
            closest_index = i

    return closest_index


def check_is_ahead(pose_1, pose_2):
    """
    Checks if pose_2 is in front of the vehicle (pose_1)
    :param pose_1: must (directly) contain position and orientation
    :param pose_2: must (directly) contain position and orientation
    :return: True / False
    """
    # Distances in x and y
    dx = pose_2.position.x - pose_1.position.x
    dy = pose_2.position.y - pose_1.position.y

    # Init angle
    angle = None

    # Quadrant definition
    if dx == 0:
        if dy >= 0:
            angle = 0.5 * math.pi
        else:
            angle = 1.5 * math.pi
    elif dx > 0.0 and dy >= 0.0:
        angle = math.atan(dy / dx)
    elif dx > 0.0 >= dy:
        angle = 2 * math.pi - math.atan(-dy / dx)
    elif dx < 0.0 and dy <= 0.0:
        angle = math.pi + math.atan(dy / dx)
    else:
        angle = math.pi - math.atan(-dy / dx)

    # Transformation from quaternion to euler
    quaternion = (pose_1.orientation.x,
                  pose_1.orientation.y,
                  pose_1.orientation.z,
                  pose_1.orientation.w)
    euler = tf.transformations.euler_from_quaternion(quaternion)

    car_angle = euler[2]
    # Normalize orientation
    while car_angle < 0:
        car_angle += 2 * math.pi
    while car_angle > 2 * math.pi:
        car_angle -= 2 * math.pi

    assert (not 0 > car_angle and car_angle <= 2 * math.pi)

    delta_angle = abs(angle - car_angle)
    if delta_angle >= 0.5 * math.pi:
        if delta_angle <= 1.5 * math.pi:
            return False
        else:
            return True
    else:
        return True


def squared_dist(pose_1, pose_2):
    dx = pose_1.pose.position.x - pose_2.pose.position.x
    dy = pose_1.pose.position.y - pose_2.pose.position.y
    return dx * dx + dy * dy


# TODO Do we need this function?
def distance(waypoints, wp1, wp2):
    dist = 0
    dl = lambda a, b: math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)
    for i in range(wp1, wp2 + 1):
        dist += dl(waypoints[wp1].pose.pose.position, waypoints[i].pose.pose.position)
        wp1 = i
    return dist


transform_listener = tf.TransformListener()

def project_to_image_plane(point_in_world, fx=1350.0, fy=1350.0, image_width=800, image_height=600):
    """Project point from 3D world coordinates to 2D camera image location

    Args:
        point_in_world (Point): 3D location of a point in the world

    Returns:
        x (int): x coordinate of target point in image
        y (int): y coordinate of target point in image

    """

    # fx = self.config['camera_info']['focal_length_x']
    # fy = self.config['camera_info']['focal_length_y']
    # image_width = self.config['camera_info']['image_width']
    # image_height = self.config['camera_info']['image_height']

    # get transform between pose of camera and world frame
    trans = None
    rot = None
    try:
        now = rospy.Time.now()
        transform_listener.waitForTransform("/base_link", "/world", now, rospy.Duration(1.0))
        trans, rot = transform_listener.lookupTransform("/base_link", "/world", now)
    except (tf.Exception, tf.LookupException, tf.ConnectivityException):
        rospy.logerr("Failed to find camera to map transform.")
        return None

    # TODO Use transform and rotation to calculate 2D position of light in image
    if trans is not None:
        px = point_in_world.x
        py = point_in_world.y
        pz = point_in_world.z
        xt = trans[0]
        yt = trans[1]
        zt = trans[2]

        euler = tf.transformations.euler_from_quaternion(rot)
        sinyaw = math.sin(euler[2])
        cosyaw = math.cos(euler[2])

        Rnt = (
            px * cosyaw - py * sinyaw + xt,
            px * sinyaw + py * cosyaw + yt,
            pz + zt)

        x = int(fx * -Rnt[1] / Rnt[0] + image_width / 2)
        y = int(fy * -Rnt[2] / Rnt[0] + image_height / 2)

        return x, y

    else:
        return None
