#!/usr/bin/env python3
"""
restamp_odom.py
===============
Re-publica o /dog_odom com o timestamp corrigido pelo offset de clock.

O dog_odom publica com ~61s de atraso em relação ao clock do sistema.
O offset é medido automaticamente na primeira mensagem e aplicado
a todas as seguintes — mesmo método do odom_to_tf e restamp_cloud,
garantindo consistência temporal entre TF, scan e odometria.

Subscriptions:  /dog_odom           (nav_msgs/Odometry)
Publications:   /dog_odom_restamped  (nav_msgs/Odometry)
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from nav_msgs.msg import Odometry
from builtin_interfaces.msg import Time


class RestampOdom(Node):

    def __init__(self):
        super().__init__("restamp_odom")

        self._offset_ns = None

        qos_sub = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        qos_pub = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        self._pub = self.create_publisher(
            Odometry, "/dog_odom_restamped", qos_pub
        )
        self._sub = self.create_subscription(
            Odometry, "/dog_odom", self._cb, qos_sub
        )
        self.get_logger().info(
            "restamp_odom: aguardando primeira mensagem para medir offset..."
        )

    def _stamp_to_ns(self, stamp) -> int:
        return stamp.sec * 10**9 + stamp.nanosec

    def _ns_to_stamp(self, ns: int) -> Time:
        t = Time()
        t.sec = int(ns // 10**9)
        t.nanosec = int(ns % 10**9)
        return t

    def _cb(self, msg: Odometry):
        now_ns = self.get_clock().now().nanoseconds
        msg_ns = self._stamp_to_ns(msg.header.stamp)

        if self._offset_ns is None:
            self._offset_ns = now_ns - msg_ns
            self.get_logger().info(
                f"restamp_odom: offset medido = {self._offset_ns / 1e9:.3f}s"
            )

        corrected_ns = msg_ns + self._offset_ns
        msg.header.stamp = self._ns_to_stamp(corrected_ns)
        self._pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = RestampOdom()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()