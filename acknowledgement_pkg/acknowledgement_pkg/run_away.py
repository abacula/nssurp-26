import rclpy
import time
from rclpy.node import Node
from yolo_msgs.msg import HallwayAck
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
# ROS TF Transforms
from tf_transformations import euler_from_quaternion

# Any additional imports here

# Decide your node class nam
class RunAway(Node):
    def __init__(self):

        self.follow = True # Delay before turning around
        self.saw_person = False
        self.obstacle_detected = False
        self.turning = False
        self.STOP_DIST = 0.0 # Meters
        self.FORWARD_SPD = 0.5
        self.angle_goal = 0
        self.x = 0
        self.y = 0
        self.ang = 0

        # Change to have your node name
        super().__init__('run_away_node')
        self.has_seen = False

        self.publisher = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)
        self.ack_sub = self.create_subscription(HallwayAck, '/robot4/hallway_ack', self.hallway_cb, 10)
        self.subscriber = self.create_subscription(LaserScan, '/robot4/scan', self.scan_callback, 10)
         # Subscribe to the odometry (robot location?)
        self.pos_subscriber = self.create_subscription(Odometry, '/robot4/odom', self.callback_pos, 10)



        self.timer = self.create_timer(0.1, self.loop)
    
    def hallway_cb(self, msg):

        if msg.person_detected and msg.bbox_height > 70 and not self.saw_person:
            if self.follow:
                time.sleep(5)
                self.follow = False
            self.saw_person = True
            self.turning = True
            self.angle_goal = self.ang + 3.14
            if self.angle_goal > 3.14:
                self.angle_goal -= 6.28
    
    def scan_callback(self, msg):

        for distance in msg.ranges[200:340]:
            if msg.range_min < distance < msg.range_max:
                if distance < self.STOP_DIST:
                    self.obstacle_detected = True
                    break
    
    # Callback for pos sub
    def callback_pos(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        quaternion = msg.pose.pose.orientation
         # Angle converted from quaternion to euler
        (_,_,self.ang) = euler_from_quaternion([quaternion.x, quaternion.y, quaternion.z, quaternion.w])

    def loop(self):

        twist = Twist()
        if not self.saw_person:
            twist.linear.x = self.FORWARD_SPD
            #self.get_logger().info("Nobody")

        elif not self.obstacle_detected and not self.follow:
            if self.turning:
                turn_speed = 0.0
                if abs(self.angle_goal - self.ang) < 0.01:
                    self.turning = False
                else:
                    turn_speed = (self.angle_goal - self.ang) ** 2
                    if turn_speed > 2.0:
                        turn_speed = 2.0
                    if turn_speed < 0.1:
                        turn_speed = 0.1

                twist.linear.x = 0.0
                twist.angular.z = turn_speed
                #self.get_logger().info("Somebody")
                #self.get_logger().info(f"Goal Angle: {self.angle_goal}, Cur Angle: {self.ang}")
            
            else:
                twist.linear.x = self.FORWARD_SPD
                twist.angular.z = 0.0
                #self.get_logger().info("RUN AWAY")
        else:
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            #self.get_logger().info("Found Wall")

        self.publisher.publish(twist)



def main(args=None):
    rclpy.init(args=args)

    # Change to be your node class name
    node = RunAway()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()