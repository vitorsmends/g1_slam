#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy


class DogOdomRemap(Node):

    def __init__(self):
        super().__init__("dog_odom_remap")

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.sub = self.create_subscription(
            Odometry,
            "/dog_odom",
            self.callback,
            qos
        )

        self.pub = self.create_publisher(
            Odometry,
            "/dog_odom_fixed",
            qos
        )

        self.tf = TransformBroadcaster(self)

        self.get_logger().info("dog_odom remap started")

    def callback(self, msg):

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