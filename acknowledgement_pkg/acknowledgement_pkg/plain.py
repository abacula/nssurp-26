import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from yolo_msgs.msg import HallwayAck
from irobot_create_msgs.msg import AudioNote, AudioNoteVector
from builtin_interfaces.msg import Duration
from std_msgs.msg import String
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class Plain(Node):
    def __init__(self):
        super().__init__('plain_node')

        self.SPEED = 0.5                            # m/s

        self.OBSTACLE_DETECTED = False              # stop movement if obstacle detected
        self.OBS_THRESH = 0.5                       # m, distance to obstacle that triggers stop

        self.publisher = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)
        self.ack_sub = self.create_subscription(HallwayAck, '/robot4/hallway_ack', self.hallway_cb, 10)
        self.scan_sub = self.create_subscription(LaserScan, '/robot4/scan', self.scan_cb, 10)

    def hallway_cb(self, msg):
        twist = Twist()
        if self.OBSTACLE_DETECTED:
            self.get_logger().info("Obstacle detected -- stopping.")
            twist.linear.x = 0.0 # stop moving
        else:
            twist.linear.x = self.SPEED

        self.publisher.publish(twist)

    def scan_cb(self, msg):
        front_ranges = msg.ranges[220:340]
        min = msg.range_min
        max = msg.range_max
        for distance in front_ranges:
            if distance < self.OBS_THRESH and distance > min and distance < max:
                self.OBSTACLE_DETECTED = True
                return

        self.OBSTACLE_DETECTED = False

def main(args=None):
    rclpy.init(args=args)
    
    node = Plain()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()