import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from yolo_msgs.msg import HallwayAck


class SlowdownMovement(Node):
    def __init__(self):
        super().__init__('slowdown_node')

        self.FORWARD_SPD = 0.5          # m/s
        self.CONF_THRESH = 0.75
        self.TRIGGER_HEIGHT = 60        


        self.publisher = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)
        self.ack_sub = self.create_subscription(HallwayAck, '/robot4/hallway_ack', self.hallway_cb, 10)

    def hallway_cb(self, msg):
        # ignore further detections until dodge finishes
        twist = Twist()
        if (msg.person_detected
                and msg.confidence >= self.CONF_THRESH
                and msg.bbox_height > self.TRIGGER_HEIGHT):
            self.get_logger().info("Person detected -- slowing down.")
            twist.linear.x = self.get_speed(msg.bbox_height)
            if msg.bbox_height > 230:
                twist.linear.x = 0
        else:
            self.get_logger().info("No person detected -- keep moving")
            twist.linear.x = self.FORWARD_SPD
     

        self.publisher.publish(twist)

    def get_speed(self, box_height, max_speed = 0.5, min_speed=0.05):
        ratio = self.TRIGGER_HEIGHT / box_height                  # 0.0 (close) to 1.0 (far)
        return min_speed + ratio * (max_speed - min_speed)

def main(args=None):
    rclpy.init(args=args)
    node = SlowdownMovement()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()