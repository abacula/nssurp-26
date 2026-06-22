import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from irobot_create_msgs.msg import AudioNoteVector

class KillSound(Node):
    def __init__(self):
        super().__init__('kill_sound')

        self.battery_subscriber = self.create_subscription(BatteryState, '/robot4/battery_state', self.callback, 10)
        self.sound_pub = self.create_publisher(AudioNoteVector, '/robot4/cmd_audio', 10)

    def callback(self, msg):
        self.kill()
    
    def kill(self):
        audio_msg = AudioNoteVector()
        audio_msg.append = False
        self.sound_pub.publish(audio_msg)
        self.get_logger().info("Sound Killed.")

def main(args=None):
    rclpy.init(args=args)
    node = KillSound()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()