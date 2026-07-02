import rclpy
import time
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import BatteryState

# Any additional imports here

# Decide your node class name
class LightTest(Node):
    def __init__(self):
        super().__init__('light_test')

        self.LIGHT_STATE = "pulse 96"

        self.battery_subscriber = self.create_subscription(BatteryState, '/robot4/battery_state', self.callback, 10)
        self.light_pub = self.create_publisher(String, '/light_state', 10)

    def callback(self, msg):
        # light_msg = String()
        # light_msg.data = self.LIGHT_STATE
        # self.light_pub.publish(light_msg)
        # self.get_logger().info("Light State Published: %s" % self.LIGHT_STATE)

        while True:
            light_msg = String()
            light_msg.data = "fadeTo 1 0 255 1"
            self.light_pub.publish(light_msg)
            self.get_logger().info("Light State Published: %s" % light_msg.data)
            time.sleep(10.0)
            light_msg.data = "pulse 1 85 2"
            self.light_pub.publish(light_msg)
            self.get_logger().info("Light State Published: %s" % light_msg.data)
            time.sleep(10.0)

    
def main(args=None):
    rclpy.init(args=args)

    # Change to be your node class name
    node = LightTest()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()