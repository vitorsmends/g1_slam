#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy


class DogOdomReader(Node):

    def __init__(self):

        super().__init__('dog_odom_reader')

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            durability=DurabilityPolicy.VOLATILE
        )

        self.get_logger().info("Creating subscriber...")

        self.sub = self.create_subscription(
            Odometry,
            '/dog_odom',
            self.cb,
            qos
        )

        self.get_logger().info("Subscriber created. Waiting for messages...")

    def cb(self, msg):

        print("----- ODOM MESSAGE RECEIVED -----")

        print("position:")
        print(msg.pose.pose.position.x,
              msg.pose.pose.position.y,
              msg.pose.pose.position.z)

        print("orientation:")
        print(msg.pose.pose.orientation.x,
              msg.pose.pose.orientation.y,
              msg.pose.pose.orientation.z,
              msg.pose.pose.orientation.w)

        print("---------------------------------")


def main():

    rclpy.init()

    node = DogOdomReader()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()