#!/usr/bin/env python3
"""
odom_to_tf.py
=============
Converte /dog_odom em TF odom → base_link.

O dog_odom do G1 publica com um offset constante de ~61s em relação
ao clock do sistema. Medimos esse offset na primeira mensagem e o
aplicamos a todas as mensagens seguintes, mantendo consistência
temporal perfeita com o restante do sistema (TF tree, scan, etc).

Dessa forma:
  - A TF odom→base_link fica alinhada com o clock do sistema
  - O offset entre mensagens consecutivas é preservado exatamente
  - Não há interpolação incorreta no slam_toolbox
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
from builtin_interfaces.msg import Time


class OdomToTf(Node):

    def __init__(self):
        super().__init__("odom_to_tf")

        self._br = TransformBroadcaster(self)
        self._offset_ns = None  # offset em nanosegundos, medido na 1a mensagem

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        self._sub = self.create_subscription(
            Odometry, "/dog_odom", self._cb, qos
        )
        self.get_logger().info(
            "odom_to_tf: aguardando primeira mensagem para medir offset de clock..."
        )

    def _stamp_to_ns(self, stamp) -> int:
        return stamp.sec * 10**9 + stamp.nanosec

    def _ns_to_stamp(self, ns: int) -> Time:
        t = Time()
        t.sec = ns // 10**9
        t.nanosec = ns % 10**9
        return t

    def _cb(self, msg: Odometry):
        now_ns = self.get_clock().now().nanoseconds
        msg_ns = self._stamp_to_ns(msg.header.stamp)

        # Mede o offset apenas uma vez na primeira mensagem
        if self._offset_ns is None:
            self._offset_ns = now_ns - msg_ns
            offset_s = self._offset_ns / 1e9
            self.get_logger().info(
                f"odom_to_tf: offset de clock medido = {offset_s:.3f}s — "
                f"aplicando a todas as mensagens"
            )

        # Aplica o offset preservando a diferença entre mensagens
        corrected_ns = msg_ns + self._offset_ns

        t = TransformStamped()
        t.header.stamp    = self._ns_to_stamp(corrected_ns)
        t.header.frame_id = "odom"
        t.child_frame_id  = "base_link"

        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z
        t.transform.rotation      = msg.pose.pose.orientation

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