#!/usr/bin/env python3
"""
restamp_cloud.py
================
Re-publica a nuvem de pontos do Livox com o timestamp atual (ros::Time::now()).

Por quê isso é necessário:
  O Livox usa clock de hardware (PTP/GPS) que pode divergir do clock ROS,
  gerando mensagens com timestamps do passado. O pointcloud_to_laserscan
  faz um lookup de TF usando o timestamp da mensagem — se ele for mais antigo
  que os dados no buffer do TF, o nó joga fora o frame e loga TF_OLD_DATA.

  Substituir o timestamp por now() resolve isso ao custo de ignorar a latência
  exata de aquisição — aceitável para SLAM 2D em robô humanoide.

Subscriptions:  /livox/lidar         (sensor_msgs/PointCloud2)
Publications:   /livox/lidar_restamped (sensor_msgs/PointCloud2)
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import PointCloud2


class RestampCloud(Node):

    def __init__(self):
        super().__init__("restamp_cloud")

        qos_sub = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=5,
        )
        qos_pub = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=5,
        )

        self._pub = self.create_publisher(
            PointCloud2, "/livox/lidar_restamped", qos_pub
        )
        self._sub = self.create_subscription(
            PointCloud2, "/livox/lidar", self._cb, qos_sub
        )
        self.get_logger().info("restamp_cloud: iniciado — /livox/lidar → /livox/lidar_restamped")

    def _cb(self, msg: PointCloud2):
        msg.header.stamp = self.get_clock().now().to_msg()
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