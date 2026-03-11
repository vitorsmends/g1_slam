#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy


class TestRemap(Node):

    def __init__(self):
        super().__init__("test_remap")

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

        self.counter = 0

        self.get_logger().info("Waiting for dog_odom...")

    def callback(self, msg):

        self.counter += 1

        print("RECEIVED ODOM:", self.counter)

        self.pub.publish(msg)


def main():

    rclpy.init()

    node = TestRemap()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()