import rclpy
from rclpy.node import Node

from yolo_msgs.msg import Detection
from yolo_msgs.msg import DetectionArray
from irobot_create_msgs.msg import LightringLeds
from yolo_msgs.msg import HallwayAck
# Any additional imports here

# Decide your node class name
class HumanDetectionNode(Node):
    def __init__(self):

        # Change to have your node name
        super().__init__('human_detection')
        self.human_detection_sub = self.create_subscription(DetectionArray, '/yolo/detections', self.human_cb, 10)
        self.ack_pub = self.create_publisher(
            HallwayAck, '/robot4/hallway_ack', 10)    
    def human_cb(self, detections_msg):
        best_detection = None
        best_score = 0.85  # minimum threshold

        for msg in detections_msg.detections:
            if msg.class_name == 'person' and msg.score > best_score:
                best_score = msg.score
                best_detection = msg

        ack_msg = HallwayAck()
        ack_msg.header = detections_msg.header

        if best_detection is not None:
            ack_msg.person_detected = True
            ack_msg.confidence = best_detection.score
            ack_msg.track_id = best_detection.id
            ack_msg.position.x = best_detection.bbox.center.position.x
            ack_msg.position.y = best_detection.bbox.center.position.y
            ack_msg.bbox_height = best_detection.bbox.size.y
        else:
            ack_msg.person_detected = False
            ack_msg.confidence = 0.0
            ack_msg.track_id = ""

        self.ack_pub.publish(ack_msg)
        

def main(args=None):
    rclpy.init(args=args)

    # Change to be your node class name
    node = HumanDetectionNode()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()