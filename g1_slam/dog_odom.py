#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


class TestRemap(Node):

    def __init__(self):
        super().__init__("test_remap")

        self.sub = self.create_subscription(
            Odometry,
            "/dog_odom",
            self.callback,
            10
        )

        self.pub = self.create_publisher(
            Odometry,
            "/dog_odom_fixed",
            10
        )

        self.get_logger().info("Waiting for dog_odom...")

    def callback(self, msg):

        print("RECEIVED ODOM")

        self.pub.publish(msg)


def main():

    rclpy.init()

    node = TestRemap()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()