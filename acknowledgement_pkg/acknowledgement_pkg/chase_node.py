import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from yolo_msgs.msg import HallwayAck


class ChaseNode(Node):
    def __init__(self):
        super().__init__('chase_node')

        # --- Tunables ---
        self.IMAGE_WIDTH = -1    # px, TODO: find out this value
        self.CENTER_TOL = -1      # px, how close to center counts as "inline"
        self.TURN_GAIN = 0.1      # rad/s
        self.MAX_TURN = 0.5         # rad/s
        self.FORWARD_SPD = 0.65      # m/s, approach speed
        self.STOP_HEIGHT = 250.0    # px, stop once the person box is this tall (close enough)
        self.CRUISE_WHEN_IDLE = True  # drive straight when no person is seen

        self.center_x = self.IMAGE_WIDTH / 2.0
        self.latest = None          # most recent HallwayAck

        self.ack_sub = self.create_subscription(HallwayAck, '/robot4/hallway_ack', self.ack_cb, 10)
        self.publisher = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)

        self.timer = self.create_timer(0.1, self.control_loop)

    def ack_cb(self, msg):
        self.latest = msg

    def control_loop(self):
        twist = Twist()
        msg = self.latest

        # no person, keep moving straight 
        if msg is None or not msg.person_detected:
            twist.linear.x = self.FORWARD_SPD if self.CRUISE_WHEN_IDLE else 0.0
            twist.angular.z = 0.0
            self.publisher.publish(twist)
            return

        # else stuff do later


def main(args=None):
    rclpy.init(args=args)
    node = ChaseNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()