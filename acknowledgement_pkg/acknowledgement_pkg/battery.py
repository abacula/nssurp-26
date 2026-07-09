import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
import time

class Battery(Node):
    def __init__(self):

        super().__init__('battery_node')

        self.battery_subscriber = self.create_subscription(BatteryState, '/robot4/battery_state', self.callback, 10)

    def callback(self, msg):
        battery_percentage = msg.percentage * 100
        
        if battery_percentage < 20:
            self.get_logger().warn(f'Battery percentage is {battery_percentage:.2f}% !!')
        else:
            self.get_logger().info(f'Battery percentage: {battery_percentage:.2f}%')

        time.sleep(20)  # 20 sec interval

def main(args=None):
    rclpy.init(args=args)
    node = Battery()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()