import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from yolo_msgs.msg import HallwayAck


class StopMovement(Node):
    def __init__(self):
        super().__init__('stop_node')

        self.FORWARD_SPD = 0.5          # m/s
        self.CONF_THRESH = 0.75
        self.TRIGGER_HEIGHT = 60        # bbox_height that starts the dodge

        self.publisher = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)
        self.ack_sub = self.create_subscription(HallwayAck, '/robot4/hallway_ack', self.hallway_cb, 10)

    def hallway_cb(self, msg):
        twist = Twist()
        # keep rolling forward
        if (msg.person_detected
                and msg.confidence >= self.CONF_THRESH
                and msg.bbox_height > self.TRIGGER_HEIGHT):
            self.get_logger().info("Person detected -- stop moving.")
            twist.linear.x = 0.0
        else:
            self.get_logger().info("No person detected -- keep moving")
            twist.linear.x = self.FORWARD_SPD
     

        self.publisher.publish(twist)
    

def main(args=None):
    rclpy.init(args=args)
    node = StopMovement()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()