#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy


def quat_normalize(q):
    x, y, z, w = q
    n = math.sqrt(x*x + y*y + z*z + w*w)
    if n == 0.0:
        return (0.0, 0.0, 0.0, 1.0)
    return (x/n, y/n, z/n, w/n)


class RemapAndFixTF(Node):
    def __init__(self):
        super().__init__("remap_and_fix_tf")

        self.declare_parameter("in_odom", "/dog_odom")
        self.declare_parameter("out_odom", "/dog_odom_fixed")
        self.declare_parameter("in_scan", "/scan")
        self.declare_parameter("out_scan", "/scan_fixed")
        self.declare_parameter("odom_frame", "odom")
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("lidar_frame", "livox_frame")
        self.declare_parameter("normalize_quaternion", True)

        self.in_odom = self.get_parameter("in_odom").value
        self.out_odom = self.get_parameter("out_odom").value
        self.in_scan = self.get_parameter("in_scan").value
        self.out_scan = self.get_parameter("out_scan").value
        self.odom_frame = self.get_parameter("odom_frame").value
        self.base_frame = self.get_parameter("base_frame").value
        self.lidar_frame = self.get_parameter("lidar_frame").value
        self.normalize_quaternion = self.get_parameter("normalize_quaternion").value

        qos_sensor = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            self.in_odom,
            self.cb_odom,
            10
        )

        self.scan_sub = self.create_subscription(
            LaserScan,
            self.in_scan,
            self.cb_scan,
            qos_sensor
        )

        self.odom_pub = self.create_publisher(
            Odometry,
            self.out_odom,
            10
        )

        self.scan_pub = self.create_publisher(
            LaserScan,
            self.out_scan,
            qos_sensor
        )

        self.tf_broadcaster = TransformBroadcaster(self)

    def cb_odom(self, msg: Odometry):

        odom = Odometry()

        odom.header = msg.header
        odom.header.frame_id = self.odom_frame
        odom.child_frame_id = self.base_frame

        odom.pose = msg.pose
        odom.twist = msg.twist

        if self.normalize_quaternion:
            q = odom.pose.pose.orientation
            x, y, z, w = quat_normalize((q.x, q.y, q.z, q.w))
            q.x, q.y, q.z, q.w = x, y, z, w

        self.odom_pub.publish(odom)

        tf = TransformStamped()
        tf.header = odom.header
        tf.child_frame_id = self.base_frame

        tf.transform.translation.x = odom.pose.pose.position.x
        tf.transform.translation.y = odom.pose.pose.position.y
        tf.transform.translation.z = odom.pose.pose.position.z
        tf.transform.rotation = odom.pose.pose.orientation

        self.tf_broadcaster.sendTransform(tf)

    def cb_scan(self, msg: LaserScan):

        scan = LaserScan()

        scan.header = msg.header
        scan.header.frame_id = self.lidar_frame

        scan.angle_min = msg.angle_min
        scan.angle_max = msg.angle_max
        scan.angle_increment = msg.angle_increment
        scan.time_increment = msg.time_increment
        scan.scan_time = msg.scan_time
        scan.range_min = msg.range_min
        scan.range_max = msg.range_max
        scan.ranges = msg.ranges
        scan.intensities = msg.intensities

        self.scan_pub.publish(scan)


def main():
    rclpy.init()
    node = RemapAndFixTF()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()