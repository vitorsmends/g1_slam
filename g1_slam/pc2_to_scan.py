#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import PointCloud2, LaserScan
from sensor_msgs_py import point_cloud2 as pc2


class PointCloudToLaserScan(Node):
    def __init__(self):
        super().__init__("pc2_to_scan")

        self.declare_parameter("cloud_topic", "/livox/lidar")
        self.declare_parameter("scan_topic", "/scan")
        self.declare_parameter("override_frame_id", "")
        self.declare_parameter("angle_min", -math.pi)
        self.declare_parameter("angle_max", math.pi)
        self.declare_parameter("angle_increment", 0.0087)
        self.declare_parameter("range_min", 0.3)
        self.declare_parameter("range_max", 50.0)
        self.declare_parameter("min_height", -10.0)
        self.declare_parameter("max_height", 10.0)
        self.declare_parameter("use_inf", True)
        self.declare_parameter("log_every_n", 30)

        self.cloud_topic = str(self.get_parameter("cloud_topic").value)
        self.scan_topic = str(self.get_parameter("scan_topic").value)
        self.override_frame_id = str(self.get_parameter("override_frame_id").value)

        self.angle_min = float(self.get_parameter("angle_min").value)
        self.angle_max = float(self.get_parameter("angle_max").value)
        self.angle_increment = float(self.get_parameter("angle_increment").value)

        self.range_min = float(self.get_parameter("range_min").value)
        self.range_max = float(self.get_parameter("range_max").value)

        self.min_height = float(self.get_parameter("min_height").value)
        self.max_height = float(self.get_parameter("max_height").value)

        self.use_inf = bool(self.get_parameter("use_inf").value)
        self.log_every_n = int(self.get_parameter("log_every_n").value)

        if self.angle_increment <= 0.0:
            raise ValueError("angle_increment must be > 0")

        self.n_bins = int(math.floor((self.angle_max - self.angle_min) / self.angle_increment)) + 1
        if self.n_bins <= 0:
            raise ValueError("Invalid angle_min/angle_max/angle_increment")

        self.pub = self.create_publisher(LaserScan, self.scan_topic, qos_profile_sensor_data)
        self.sub = self.create_subscription(PointCloud2, self.cloud_topic, self.cb, qos_profile_sensor_data)

        self.msg_count = 0
        self.get_logger().info(
            f"Subscribing {self.cloud_topic} -> publishing {self.scan_topic} "
            f"bins={self.n_bins} angle=[{self.angle_min},{self.angle_max}] inc={self.angle_increment} "
            f"range=[{self.range_min},{self.range_max}] height=[{self.min_height},{self.max_height}]"
        )

    def cb(self, msg: PointCloud2):
        self.msg_count += 1

        scan = LaserScan()
        scan.header.stamp = msg.header.stamp
        scan.header.frame_id = self.override_frame_id if self.override_frame_id else msg.header.frame_id

        scan.angle_min = float(self.angle_min)
        scan.angle_max = float(self.angle_max)
        scan.angle_increment = float(self.angle_increment)

        scan.time_increment = 0.0
        scan.scan_time = 0.0

        scan.range_min = float(self.range_min)
        scan.range_max = float(self.range_max)

        if self.use_inf:
            ranges = [float("inf")] * self.n_bins
        else:
            ranges = [scan.range_max] * self.n_bins

        total = 0
        used = 0
        rejected_naninf = 0
        rejected_height = 0
        rejected_range = 0
        rejected_angle = 0

        for x, y, z in pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=False):
            total += 1

            if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
                rejected_naninf += 1
                continue

            if z < self.min_height or z > self.max_height:
                rejected_height += 1
                continue

            r = math.hypot(x, y)
            if r < self.range_min or r > self.range_max:
                rejected_range += 1
                continue

            a = math.atan2(y, x)
            if a < self.angle_min or a > self.angle_max:
                rejected_angle += 1
                continue

            idx = int((a - self.angle_min) / self.angle_increment)
            if 0 <= idx < self.n_bins:
                if r < ranges[idx]:
                    ranges[idx] = r
                used += 1

        scan.ranges = ranges
        scan.intensities = []

        if self.log_every_n > 0 and (self.msg_count % self.log_every_n) == 0:
            finite_bins = sum(1 for v in ranges if math.isfinite(v))
            self.get_logger().info(
                f"[PC2->SCAN] msgs={self.msg_count} pts={total} used={used} "
                f"finite_bins={finite_bins}/{self.n_bins} "
                f"rej(nan/inf)={rejected_naninf} rej(height)={rejected_height} "
                f"rej(range)={rejected_range} rej(angle)={rejected_angle} "
                f"frame='{scan.header.frame_id}'"
            )

        self.pub.publish(scan)


def main():
    rclpy.init()
    node = PointCloudToLaserScan()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()