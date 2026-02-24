#!/usr/bin/env python3
import math
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_


def quat_to_yaw_xyzw(qx: float, qy: float, qz: float, qw: float) -> float:
    siny_cosp = 2.0 * (qw * qz + qx * qy)
    cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
    return math.atan2(siny_cosp, cosy_cosp)


class LowStateToDogOdom(Node):
    def __init__(self):
        super().__init__("lowstate_to_dog_odom")

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        self.pub = self.create_publisher(Odometry, "/dog_odom", qos)
        self.cmd_sub = self.create_subscription(Twist, "/cmd_vel", self._cmd_cb, qos)

        self._pos_x = 0.0
        self._pos_y = 0.0
        self._pos_z = 0.0
        self._yaw = 0.0

        self._vx_cmd = 0.0
        self._vy_cmd = 0.0
        self._wz_cmd = 0.0

        self._last_t = time.time()

        ChannelFactoryInitialize(0)
        self.dds_sub = ChannelSubscriber("rt/lowstate", LowState_)
        self.dds_sub.Init(self._dds_cb)

        self.get_logger().info("Subscribed to DDS rt/lowstate (domain 0), publishing /dog_odom")

    def _cmd_cb(self, msg: Twist):
        self._vx_cmd = float(msg.linear.x)
        self._vy_cmd = float(msg.linear.y)
        self._wz_cmd = float(msg.angular.z)

    def _dds_cb(self, msg: LowState_):
        now = time.time()
        dt = now - self._last_t
        if dt <= 0.0:
            dt = 0.0
        self._last_t = now

        imu = msg.imu_state
        q = [float(x) for x in imu.quaternion]

        if abs(q[0]) >= abs(q[3]):
            qw, qx, qy, qz = q[0], q[1], q[2], q[3]
        else:
            qx, qy, qz, qw = q[0], q[1], q[2], q[3]

        self._yaw = quat_to_yaw_xyzw(qx, qy, qz, qw)

        cos_y = math.cos(self._yaw)
        sin_y = math.sin(self._yaw)
        vx_w = self._vx_cmd * cos_y - self._vy_cmd * sin_y
        vy_w = self._vx_cmd * sin_y + self._vy_cmd * cos_y

        self._pos_x += vx_w * dt
        self._pos_y += vy_w * dt

        odom = Odometry()
        odom.header.stamp = self.get_clock().now().to_msg()
        odom.header.frame_id = "odom"
        odom.child_frame_id = "base_link"

        odom.pose.pose.position.x = self._pos_x
        odom.pose.pose.position.y = self._pos_y
        odom.pose.pose.position.z = self._pos_z

        odom.pose.pose.orientation.x = qx
        odom.pose.pose.orientation.y = qy
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw

        odom.twist.twist.linear.x = self._vx_cmd
        odom.twist.twist.linear.y = self._vy_cmd
        odom.twist.twist.angular.z = self._wz_cmd

        self.pub.publish(odom)


def main():
    rclpy.init()
    node = LowStateToDogOdom()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()