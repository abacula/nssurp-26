import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from yolo_msgs.msg import HallwayAck


class DodgeNode(Node):
    def __init__(self):
        super().__init__('dodge_node')

        self.FORWARD_SPD = 0.5          # m/s
        self.TURN_RATE = 0.4            # rad/s
        self.DODGE_DURATION = 3.0       # s

        self.CONF_THRESH = 0.75
        self.TRIGGER_HEIGHT = 60        # bbox_height that starts the dodge

        # true while the dodge is in progress
        self.dodging = False
        self.dodge_timer = None

        self.publisher = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)
        self.ack_sub = self.create_subscription(HallwayAck, '/robot4/hallway_ack', self.hallway_cb, 10)

        self.timer = self.create_timer(0.1, self.control_loop)

    def hallway_cb(self, msg):
        # ignore further detections until dodge finishes
        if self.dodging:
            self.get_logger().info("here 1")
            return
        self.get_logger().info("here 2")
        if (msg.person_detected
                and msg.confidence >= self.CONF_THRESH
                and msg.bbox_height > self.TRIGGER_HEIGHT):
            self.get_logger().info("Person detected -- dodging right.")
            self.dodging = True

            self.dodge_timer = self.create_timer(self.DODGE_DURATION, self.stop_dodge)

    def stop_dodge(self):
        self.get_logger().info("Dodge complete -- driving straight.")
        self.dodging = False
        if self.dodge_timer is not None:
            self.dodge_timer.cancel()
            self.dodge_timer = None

    def control_loop(self):
        # keep rolling forward
        
        twist = Twist()
        twist.linear.x = self.FORWARD_SPD
        self.get_logger().info("here 3")

        # curve right while dodging; otherwise go straight
        if self.dodging:
            twist.angular.z = -self.TURN_RATE
        else:
            twist.angular.z = 0.0

        self.publisher.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = DodgeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()