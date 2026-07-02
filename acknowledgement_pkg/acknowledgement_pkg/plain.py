import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from yolo_msgs.msg import HallwayAck
from irobot_create_msgs.msg import AudioNote, AudioNoteVector
from builtin_interfaces.msg import Duration
from std_msgs.msg import String


class Plain(Node):
    def __init__(self):
        super().__init__('plain_node')

        self.publisher = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)
        self.ack_sub = self.create_subscription(HallwayAck, '/robot4/hallway_ack', self.hallway_cb, 10)

    def hallway_cb(self, msg):
        twist = Twist()
        twist.linear.x = 0.5
        self.publisher.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    
    node = Plain()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()