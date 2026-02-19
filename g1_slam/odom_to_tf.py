import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
import math

class OdomToTF2D(Node):
    def __init__(self):
        super().__init__('odom_to_tf_node')
        
        # 1. Importante: Declarar o parâmetro para o nó aceitar sim_time
        self.declare_parameter('use_sim_time', True)
        
        # 2. O Broadcaster usará o clock do nó (que segue a bag se use_sim_time=True)
        self.br = TransformBroadcaster(self)
        
        self.subscription = self.create_subscription(
            Odometry,
            '/dog_odom',
            self.handle_odom,
            10)
        
        self.get_logger().info('Nó OdomToTF 2D pronto e sincronizado.')

    def handle_odom(self, msg):
        t = TransformStamped()
        
        # Sincronização: Usa o tempo EXATO da mensagem da bag
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'robot_center'

        # Translação Planar
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = 0.0 

        # Cálculo do Yaw (Z) está correto
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        # Rotação Planar (sem Roll e Pitch)
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = math.sin(yaw / 2.0)
        t.transform.rotation.w = math.cos(yaw / 2.0)

        self.br.sendTransform(t)

def main():
    rclpy.init()
    node = OdomToTF2D()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()