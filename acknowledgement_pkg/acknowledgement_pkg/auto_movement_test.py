import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class DoorwayNavigator(Node):
    def __init__(self):
        super().__init__('auto_move')
        
        # STATE = 0: Driving straight out of the room doorway
        # STATE = 1: Wall detected, pivoting left
        # STATE = 2: Hallway cruise state
        self.STATE = 0 
        self.STOP_DIST = 0.5            # (meters)
        self.FORWARD_SPD = 0.5          # speed
        
        self.publisher = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)
        self.subscriber = self.create_subscription(LaserScan, '/robot4/scan', self.scan_callback, 10)
        
        self.timer = self.create_timer(0.1, self.control_loop)
        self.twist = Twist()

    def scan_callback(self, msg):
        valid_min = msg.range_min
        valid_max = msg.range_max
        
        front_cone = msg.ranges[200:340] 
        
        # flag
        obstacle_detected = False
        
        for distance in front_cone:
            if valid_min < distance < valid_max:
                if distance < self.STOP_DIST:
                    obstacle_detected = True
                    break
        
        if self.STATE == 0 and obstacle_detected:
            self.get_logger().info("Wall detected.")
            self.STATE = 1 
            
    def control_loop(self):
        # drive forward
        if self.STATE == 0:
            self.twist.linear.x = self.FORWARD_SPD
            self.twist.angular.z = 0.0
            
        # pivot left
        elif self.STATE == 1:
            self.twist.linear.x = 0.0
            self.twist.angular.z = 0.5
            
            # turn for 3 secs
            self.create_timer(3.2, self.transition_to_hallway)
            self.STATE = 2
            
        elif self.STATE == 2:
            pass 

        # hallway cruise
        elif self.STATE == 3:
            self.twist.linear.x = self.FORWARD_SPD
            self.twist.angular.z = 0.0
            
        self.publisher.publish(self.twist)

    def transition_to_hallway(self):
        self.get_logger().info("Turn complete. Driving down hallway.")
        self.STATE = 3

def main(args=None):
    rclpy.init(args=args)
    node = DoorwayNavigator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()