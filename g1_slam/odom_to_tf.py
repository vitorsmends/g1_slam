#!/usr/bin/env python3
"""
odom_to_tf.py
=============
Converte /dog_odom (nav_msgs/Odometry) em TF odom → base_link.

O Unitree G1 publica /dog_odom com:
  frame_id:       odom
  child_frame_id: robot_center

Mas nunca gera a TF correspondente. O slam_toolbox precisa de
odom → base_link no TF tree para funcionar.

Este nó:
  1. Lê /dog_odom
  2. Publica TF: odom → base_link  (remapeia robot_center → base_link
     pois base_link é o frame raiz do corpo do robô)
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


class OdomToTf(Node):

    def __init__(self):
        super().__init__("odom_to_tf")

        self._br = TransformBroadcaster(self)

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        self._sub = self.create_subscription(
            Odometry, "/dog_odom", self._cb, qos
        )
        self.get_logger().info(
            "odom_to_tf: publicando TF odom → base_link a partir de /dog_odom"
        )

    def _cb(self, msg: Odometry):
        t = TransformStamped()
        t.header.stamp    = msg.header.stamp
        t.header.frame_id = "odom"       # pai
        t.child_frame_id  = "base_link"  # filho (robot_center == base_link)

        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z

        t.transform.rotation = msg.pose.pose.orientation

        self._br.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = OdomToTf()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()