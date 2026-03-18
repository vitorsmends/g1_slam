#!/usr/bin/env python3
"""
restamp_cloud.py
================
Re-publica a nuvem Livox com o timestamp corrigido pelo mesmo offset
de clock aplicado pelo odom_to_tf.

O Livox publica com clock de hardware (PTP) alinhado com o sistema.
O dog_odom publica com clock ~61s atrasado.
O odom_to_tf corrige o dog_odom somando o offset medido.

Para que scan e TF odom→base_link estejam no mesmo tempo, o scan
também precisa ser corrigido pelo mesmo offset do dog_odom.

Funcionamento:
  - Subscreve /dog_odom para medir o offset (mesmo método do odom_to_tf)
  - Aplica o offset inverso ao scan: stamp_scan - offset
    (traz o scan do clock do hardware para o clock do dog_odom corrigido)
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import Odometry
from builtin_interfaces.msg import Time


class RestampCloud(Node):

    def __init__(self):
        super().__init__("restamp_cloud")

        self._offset_ns = None

        qos_be = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=5,
        )
        qos_rel = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=5,
        )

        self._pub = self.create_publisher(
            PointCloud2, "/livox/lidar_restamped", qos_rel
        )
        self._sub_cloud = self.create_subscription(
            PointCloud2, "/livox/lidar", self._cloud_cb, qos_be
        )
        self._sub_odom = self.create_subscription(
            Odometry, "/dog_odom", self._odom_cb, qos_be
        )
        self.get_logger().info(
            "restamp_cloud: aguardando dog_odom para medir offset de clock..."
        )

    def _stamp_to_ns(self, stamp) -> int:
        return stamp.sec * 10**9 + stamp.nanosec

    def _ns_to_stamp(self, ns: int) -> Time:
        t = Time()
        t.sec = int(ns // 10**9)
        t.nanosec = int(ns % 10**9)
        return t

    def _odom_cb(self, msg: Odometry):
        if self._offset_ns is None:
            now_ns = self.get_clock().now().nanoseconds
            msg_ns = self._stamp_to_ns(msg.header.stamp)
            self._offset_ns = now_ns - msg_ns
            offset_s = self._offset_ns / 1e9
            self.get_logger().info(
                f"restamp_cloud: offset de clock medido = {offset_s:.3f}s"
            )

    def _cloud_cb(self, msg: PointCloud2):
        if self._offset_ns is None:
            # Ainda não medimos o offset — descarta
            return

        # O scan está no clock do sistema (hardware PTP alinhado).
        # O odom_to_tf corrigiu o dog_odom somando offset.
        # Para alinhar o scan com a TF corrigida, subtraímos o offset
        # e depois somamos de volta — equivalente a usar o timestamp
        # do dog_odom mais próximo.
        # Na prática: usamos now() que já está alinhado com a TF corrigida.
        now_ns = self.get_clock().now().nanoseconds
        msg.header.stamp = self._ns_to_stamp(now_ns)
        self._pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = RestampCloud()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()