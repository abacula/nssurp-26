import rclpy
from rclpy.node import Node

# Any additional imports here

# Decide your node class name
class PatrolNode(Node):
    def __init__(self):

        # Change to have your node name
        super().__init__('patrol_node')

        self.cmd_vel_pub = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)
        self.detection_sub = self.create_subscription(DetectionArray, '/yolo/detections', self.detection_cb, 10)
        
        # State
        self.person_detected = False
        self.get_logger().info("Patrol started")

    def detection_cb(self, msg):
        for d in msg.detections:
            if d.class_name == 'person' and d.score > 0.6:
                if not self.person_detected:
                    self.get_logger().info("Person detected — stopping")
                    self.last_ack_time = self.get_clock().now()
                self.person_detected = True
                return
        self.person_detected = False

def main(args=None):
    rclpy.init(args=args)

    # Change to be your node class name
    node = PatrolNode()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()