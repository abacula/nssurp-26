import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from yolo_msgs.msg import HallwayAck
from irobot_create_msgs.msg import AudioNote, AudioNoteVector
from builtin_interfaces.msg import Duration
from std_msgs.msg import String
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from tf_transformations import euler_from_quaternion

class PlainOdom(Node):
    def __init__(self):
        super().__init__('plain_odom')

        self.SPEED = 0.5                            # m/s

        self.OBSTACLE_DETECTED = False              # stop movement if obstacle detected
        self.OBS_THRESH = 0.5                       # m, distance to obstacle that triggers stop
        self.ANG_THRESH = 0.02                       # rad, angle that triggers stop

        self.PI = 3.141592653589793
        self.ang = 0
        self.ang_offset = 0
        self.got_offset = False

        self.publisher = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)
        self.ack_sub = self.create_subscription(HallwayAck, '/robot4/hallway_ack', self.hallway_cb, 10)
        self.scan_sub = self.create_subscription(LaserScan, '/robot4/scan', self.scan_cb, 10)
        self.odom_sub = self.create_subscription(Odometry, '/robot4/odom', self.odom_cb, 10)

    def hallway_cb(self, msg):
        twist = Twist()
        if self.OBSTACLE_DETECTED:
            self.get_logger().info("Obstacle detected -- stopping.")
            twist.linear.x = 0.0 # stop moving
        elif self.got_offset:
            twist.linear.x = self.SPEED
        
        if self.ang > self.ANG_THRESH:
            twist.angular.z = -0.15
            self.get_logger().info("Turning right to correct orientation.")
        elif self.ang < -self.ANG_THRESH:
            twist.angular.z = 0.15
            self.get_logger().info("Turning left to correct orientation.")
        else:
            self.get_logger().info(str(round(self.ang,3)))

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

    def odom_cb(self, msg):
        quaternion = msg.pose.pose.orientation
         # Angle converted from quaternion to euler
        (_,_,ang) = euler_from_quaternion([quaternion.x, quaternion.y, quaternion.z, quaternion.w])

        if self.got_offset is False:
            self.ang_offset = -ang
            self.got_offset = True

        ang += self.ang_offset
        
        if ang < -self.PI:
            self.ang = ang + (2*self.PI)
        else:
            self.ang = ang

def main(args=None):
    rclpy.init(args=args)
    
    node = PlainOdom()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()