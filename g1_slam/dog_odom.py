import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

class DogOdomReader(Node):
    def __init__(self):
        super().__init__('dog_odom_simple_reader')

        # Perfil SensorData: Frequentemente resolve problemas onde o echo funciona mas o script não.
        # Ele é mais tolerante a redes Wi-Fi e altas frequências.
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT, # Tente mudar para RELIABLE se não funcionar
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=5
        )

        self.subscription = self.create_subscription(
            Odometry,
            '/dog_odom',
            self.listener_callback,
            qos_profile)
        
        # Timer apenas para você saber que o nó não travou
        self.timer = self.create_timer(2.0, self.timer_check)
        self.get_logger().info('>>> Nó iniciado. Aguardando mensagens em /dog_odom...')

    def timer_check(self):
        self.get_logger().info('Aguardando dados... (Verifique se o robô está se movendo ou se o serviço de odom está ativo)')

    def listener_callback(self, msg):
        # Se chegar aqui, a conexão foi bem sucedida!
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        self.get_logger().info(f'RECEBIDO - Pos X: {x:.3f}, Pos Y: {y:.3f}')

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