#!/usr/bin/env python3

import rclpy
import time

from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

from rclpy.qos import qos_profile_sensor_data


class DogOdomDebug(Node):

    def __init__(self):
        super().__init__("dog_odom_debug")

        self.get_logger().info("NODE STARTED")

        self.last_msg = None
        self.last_rx_time = None
        self.rx_counter = 0
        self.pub_counter = 0

        self.get_logger().info("CREATING SUBSCRIBER")

        self.sub = self.create_subscription(
            Odometry,
            "/dog_odom",
            self.callback,
            qos_profile_sensor_data
        )

        self.get_logger().info("SUBSCRIBER CREATED")

        self.get_logger().info("CREATING PUBLISHER")

        self.pub = self.create_publisher(
            Odometry,
            "/dog_odom_fixed",
            10
        )

        self.get_logger().info("PUBLISHER CREATED")

        self.tf = TransformBroadcaster(self)

        self.get_logger().info("CREATING TIMER")

        self.timer = self.create_timer(
            0.02,   # 50 Hz
            self.timer_callback
        )

        self.get_logger().info("TIMER STARTED (50Hz)")

    def callback(self, msg):

        now = time.time()

        if self.last_rx_time is not None:
            dt = now - self.last_rx_time
            self.get_logger().info(f"DDS MESSAGE RECEIVED dt={dt:.6f}s")

        else:
            self.get_logger().info("FIRST DDS MESSAGE RECEIVED")

        self.last_rx_time = now
        self.last_msg = msg

        self.rx_counter += 1

        self.get_logger().info(f"TOTAL DDS MESSAGES: {self.rx_counter}")

    def timer_callback(self):

        if self.last_msg is None:

            self.get_logger().warn(
                "TIMER RUNNING BUT NO ODOM RECEIVED YET"
            )

            return

        msg = self.last_msg

        odom = Odometry()

        odom.header.stamp = self.get_clock().now().to_msg()
        odom.header.frame_id = "odom"
        odom.child_frame_id = "base_link"

        odom.pose = msg.pose
        odom.twist = msg.twist

        self.pub.publish(odom)

        self.pub_counter += 1

        self.get_logger().info(
            f"PUBLISHED ODOM_FIXED #{self.pub_counter}"
        )

        tf = TransformStamped()

        tf.header.stamp = odom.header.stamp
        tf.header.frame_id = "odom"
        tf.child_frame_id = "base_link"

        tf.transform.translation.x = odom.pose.pose.position.x
        tf.transform.translation.y = odom.pose.pose.position.y
        tf.transform.translation.z = odom.pose.pose.position.z

        tf.transform.rotation = odom.pose.pose.orientation

        self.tf.sendTransform(tf)

        self.get_logger().info("TF SENT odom → base_link")


def main():

    rclpy.init()

    node = DogOdomDebug()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()