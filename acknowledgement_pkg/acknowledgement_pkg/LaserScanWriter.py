import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from rclpy.qos import qos_profile_sensor_data


class LaserScanWriter(Node):
    def __init__(self):

        # Change to have your node name
        super().__init__('laser_scan_writer')

        self.scan_sub = self.create_subscription(LaserScan, '/robot4/scan', self.scan_callback, 10)
        self.got = False
        self.wait_count = 0

    def scan_callback(self,msg):
        n = len(msg.ranges)
        i = 0
        
        if self.got is False:
            self.got = True
            with open("laser_scan.csv", "w") as f:
                while i<n:
                    scan_val = msg.ranges[i]
                    f.write(str(scan_val) + ", index: " + str(i) + "\n")
                    i += 1

def main(args=None):
    rclpy.init(args=args)

    # Change to be your node class name
    node = LaserScanWriter()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()