#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from rclpy.qos import qos_profile_sensor_data


class DogOdomReader(Node):

    def __init__(self):

        super().__init__('dog_odom_reader')

        self.get_logger().info("Creating subscriber...")

        self.sub = self.create_subscription(
            Odometry,
            '/dog_odom',
            self.cb,
            qos_profile_sensor_data
        )

        self.get_logger().info("Subscriber ready. Waiting for data...")

    def cb(self, msg):

        print("\nODOM RECEIVED")
        print("position:",
              msg.pose.pose.position.x,
              msg.pose.pose.position.y,
              msg.pose.pose.position.z)

        print("orientation:",
              msg.pose.pose.orientation.x,
              msg.pose.pose.orientation.y,
              msg.pose.pose.orientation.z,
              msg.pose.pose.orientation.w)


def main():

    rclpy.init()
    node = DogOdomReader()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()