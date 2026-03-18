#!/usr/bin/env python3
"""
restamp_odom.py
===============
Re-publica o /dog_odom com o timestamp atual (ros::now()).

O dog_odom chega com timestamp ~13 minutos no passado em relação ao
/clock do sistema, causando dois problemas:
  1. RViz descarta a mensagem (timestamp fora da janela de exibição)
  2. slam_toolbox ignora a odometria por estar fora do TF buffer

Este nó corrige o header.stamp mantendo todos os outros campos intactos.

Subscriptions:  /dog_odom          (nav_msgs/Odometry)
Publications:   /dog_odom_restamped (nav_msgs/Odometry)
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from nav_msgs.msg import Odometry


class RestampOdom(Node):

    def __init__(self):
        super().__init__("restamp_odom")

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
            "restamp_odom: iniciado — /dog_odom → /dog_odom_restamped"
        )

    def _cb(self, msg: Odometry):
        msg.header.stamp = self.get_clock().now().to_msg()
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