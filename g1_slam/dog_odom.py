#!/usr/bin/env python3

import rclpy
import time
from rclpy.node import Node

from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy, qos_profile_sensor_data


class DogOdomRemap(Node):

    def __init__(self):
        super().__init__("dog_odom_remap")

        # QoS variantes
        qos_reliable = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        qos_best_effort = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # Subscribers múltiplos
        self.sub1 = self.create_subscription(
            Odometry,
            "/dog_odom",
            self.callback,
            qos_reliable
        )

        self.sub2 = self.create_subscription(
            Odometry,
            "/dog_odom",
            self.callback,
            qos_best_effort
        )

        self.sub3 = self.create_subscription(
            Odometry,
            "/dog_odom",
            self.callback,
            qos_profile_sensor_data
        )

        # Publisher
        self.pub = self.create_publisher(
            Odometry,
            "/dog_odom_fixed",
            10
        )

        self.tf = TransformBroadcaster(self)

        self.last_pub = 0.0

        self.get_logger().info("dog_odom remap started")

    def callback(self, msg):

        print("ODOM RECEIVED")

        now = time.time()

        if now - self.last_pub < 0.02:
            return

        self.last_pub = now

        odom = Odometry()

        odom.header.stamp = self.get_clock().now().to_msg()
        odom.header.frame_id = "odom"
        odom.child_frame_id = "base_link"

        odom.pose = msg.pose
        odom.twist = msg.twist

        self.pub.publish(odom)

        tf = TransformStamped()

        tf.header.stamp = odom.header.stamp
        tf.header.frame_id = "odom"
        tf.child_frame_id = "base_link"

        tf.transform.translation.x = odom.pose.pose.position.x
        tf.transform.translation.y = odom.pose.pose.position.y
        tf.transform.translation.z = odom.pose.pose.position.z

        tf.transform.rotation = odom.pose.pose.orientation

        self.tf.sendTransform(tf)


def main():

    rclpy.init()

    node = DogOdomRemap()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()