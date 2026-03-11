#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class DogOdomRemap(Node):

    def __init__(self):

        super().__init__('dog_odom_remap')

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.sub = self.create_subscription(
            Odometry,
            '/dog_odom',
            self.cb,
            qos
        )

        self.pub = self.create_publisher(
            Odometry,
            '/dog_odom_fixed',
            10
        )

        self.get_logger().info("dog_odom subscriber started")

    def cb(self, msg):

        self.get_logger().info("ODOM RECEIVED")

        self.pub.publish(msg)

def main():

    rclpy.init()
    node = DogOdomRemap()
    rclpy.spin(node)

if __name__ == "__main__":
    main()