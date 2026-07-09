import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import BatteryState

class KillLights(Node):
    def __init__(self):
        super().__init__('kill_lights')

        self.LIGHT_STATE = "die"

        self.battery_subscriber = self.create_subscription(BatteryState, '/robot4/battery_state', self.callback, 10)
        self.light_pub = self.create_publisher(String, '/light_state', 10)

    def callback(self, msg):
        light_msg = String()
        light_msg.data = self.LIGHT_STATE
        self.light_pub.publish(light_msg)

def main(args=None):
    rclpy.init(args=args)
    node = KillLights()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()