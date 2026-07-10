import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from irobot_create_msgs.msg import LightringLeds
from rclpy.qos import qos_profile_sensor_data
import time

class Battery(Node):
    def __init__(self):

        super().__init__('battery_node')

        self.battery_subscriber = self.create_subscription(BatteryState, '/robot4/battery_state', self.callback, 10)
        self.led_publish = self.create_publisher(LightringLeds, '/robotN/cmd_lightring', qos_profile_sensor_data)

    def callback(self, msg):
        battery_percentage = msg.percentage * 100
        
        if battery_percentage < 20:
            self.get_logger().warn(f'Battery percentage is {battery_percentage:.2f}% !!')
        else:
            self.get_logger().info(f'Battery percentage: {battery_percentage:.2f}%')
        
        if battery_percentage < 40:
            led_msg = LightringLeds()
            for i in range(6):
                led_msg.leds[i].red = 255
                led_msg.leds[i].blue = 255
                led_msg.leds[i].green = 0
            self.led_publish.publish(led_msg)
        
        time.sleep(20)  # 20 sec interval

def main(args=None):
    rclpy.init(args=args)
    node = Battery()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()