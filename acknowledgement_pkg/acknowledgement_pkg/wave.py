import rclpy
import time
from rclpy.node import Node
from yolo_msgs.msg import HallwayAck
from geometry_msgs.msg import Twist

# Any additional imports here

# Decide your node class name
class Wave(Node):
    def __init__(self):

        self.person_detected = False
        self.speed = 0.5
        self.waving = False
        self.waved = False

        # Change to have your node name
        super().__init__('wave_node')
        self.has_seen = False

        self.publisher = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)
        self.ack_sub = self.create_subscription(HallwayAck, '/robot4/hallway_ack', self.hallway_cb, 10)

        self.timer = self.create_timer(0.1, self.loop)
    
    def hallway_cb(self, msg):

        if msg.person_detected and msg.bbox_height > 70 and not self.waved:
            self.person_detected = True
            self.wave()
        else:
            self.person_detected = False

    def wave(self):

        self.waving = True
        self.waved = True

        twist = Twist()
        twist.linear.x = 0.0
        
        # Turn left
        twist.angular.z = 1
        self.publisher.publish(twist)
        time.sleep(0.5)

        # Wave left
        twist.angular.z = 0.5
        self.publisher.publish(twist)
        time.sleep(0.5)
        
        # Wave right
        twist.angular.z = -0.5
        self.publisher.publish(twist)
        time.sleep(0.5)
        twist.angular.z = -0.5
        self.publisher.publish(twist)
        time.sleep(0.5)

        # Return left
        twist.angular.z = 0.5
        self.publisher.publish(twist)
        time.sleep(0.5)

        # Turn right
        twist.angular.z = 1
        self.publisher.publish(twist)
        time.sleep(0.5)
        
        twist.angular.z = 0.0
        self.publisher.publish(twist)

        self.waving = False

    def loop(self):
        
        twist = Twist()
        twist.linear.x = 0.5
        if self.person_detected or self.waving:
            twist.linear.x = 0.0

        self.publisher.publish(twist)


def main(args=None):
    rclpy.init(args=args)

    # Change to be your node class name
    node = Wave()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()