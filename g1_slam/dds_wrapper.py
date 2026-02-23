#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion
from builtin_interfaces.msg import Time as RosTime

# Unitree DDS
from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_


def _ros_time_from_timespec(sec: int, nanosec: int) -> RosTime:
    t = RosTime()
    t.sec = int(sec)
    t.nanosec = int(nanosec)
    return t


class SportModeStateToOdom(Node):
    def __init__(self):
        super().__init__("sportmodestate_to_odom")

        # ROS publisher
        self.pub = self.create_publisher(Odometry, "/dog_odom", 10)

        # DDS init + subscriber
        ChannelFactoryInitialize(0)  # domain_id=0 (ajuste se necessário)
        self.sub = ChannelSubscriber("rt/sportmodestate", SportModeState_)
        self.sub.Init(self._dds_cb)

        self.get_logger().info("Subscribed to DDS rt/sportmodestate, publishing /dog_odom")

    def _dds_cb(self, msg: SportModeState_):
        odom = Odometry()

        # Header time from DDS stamp
        odom.header.stamp = _ros_time_from_timespec(msg.stamp.sec, msg.stamp.nanosec)
        odom.header.frame_id = "odom"
        odom.child_frame_id = "base_link"

        # Position
        odom.pose.pose.position.x = float(msg.position[0])
        odom.pose.pose.position.y = float(msg.position[1])
        odom.pose.pose.position.z = float(msg.position[2])

        # Orientation from IMU quaternion
        # OBS: a ordem pode ser [w,x,y,z] ou [x,y,z,w] — confirme no teste.
        q = msg.imu_state.quaternion
        odom.pose.pose.orientation = Quaternion(
            w=float(q[0]),
            x=float(q[1]),
            y=float(q[2]),
            z=float(q[3]),
        )

        # Linear velocity
        odom.twist.twist.linear.x = float(msg.velocity[0])
        odom.twist.twist.linear.y = float(msg.velocity[1])
        odom.twist.twist.linear.z = float(msg.velocity[2])

        # Angular velocity (yaw rate)
        odom.twist.twist.angular.z = float(msg.yaw_speed)

        self.pub.publish(odom)


def main():
    rclpy.init()
    node = SportModeStateToOdom()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()