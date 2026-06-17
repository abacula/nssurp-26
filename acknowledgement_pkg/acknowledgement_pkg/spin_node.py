import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from yolo_msgs.msg import HallwayAck


class SpinNode(Node):

    def __init__(self):
        super().__init__('spin_node')

        self.FORWARD_SPEED = 0.5
        self.SPIN_SPEED = 1.0

        self.CONF_THRESH = 0.75
        self.TRIGGER_HEIGHT = 100

        self.person_seen = False

        self.pub = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)
        self.ack_sub = self.create_subscription(HallwayAck, '/robot4/hallway_ack', self.ack_cb, 10)

        self.control_timer = self.create_timer(0.1, self.control_loop)

    def ack_cb(self, msg):

        if self.person_seen:
            return

        if (
            msg.person_detected
            and msg.confidence >= self.CONF_THRESH
            and msg.bbox_height > self.TRIGGER_HEIGHT
        ):
            self.get_logger().info("Person detected -- Spin")
            self.person_seen = True

    def control_loop(self):

        twist = Twist()

        if self.person_seen:
            # spin and keep spinning
            twist.linear.x = 0.0
            twist.angular.z = self.SPIN_SPEED
        else:
            # forward
            twist.linear.x = self.FORWARD_SPEED
            twist.angular.z = 0.0

        self.pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = SpinNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()