import rclpy
from rclpy.node import Node

# Any additional imports here

# Decide your node class name
class <NODE CLASS NAME>(Node):
    def __init__(self):

        # Change to have your node name
        super().__init__('<NODE NAME>')

def main(args=None):
    rclpy.init(args=args)

    # Change to be your node class name
    node = <NODE CLASS NAME>()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()