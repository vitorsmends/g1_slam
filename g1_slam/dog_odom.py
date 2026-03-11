import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

class DogOdomReader(Node):
    def __init__(self):
        super().__init__('dog_odom_simple_reader')

        # Configurando o QoS exatamente para bater com o Publisher
        # Reliability: RELIABLE (baseado no seu log)
        # Durability: VOLATILE
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.subscription = self.create_subscription(
            Odometry,
            '/dog_odom',
            self.listener_callback,
            qos_profile)
        
        self.get_logger().info('Iniciando leitura do tópico /dog_odom...')

    def listener_callback(self, msg):
        # Extraindo informações básicas
        pos = msg.pose.pose.position
        ori = msg.pose.pose.orientation
        
        self.get_logger().info(
            f'\n--- ODOMETRIA ---\n'
            f'Posição: x={pos.x:.2f}, y={pos.y:.2f}, z={pos.z:.2f}\n'
            f'Orientação (Quaternion): z={ori.z:.2f}, w={ori.w:.2f}'
        )

def main(args=None):
    rclpy.init(args=args)
    node = DogOdomReader()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()