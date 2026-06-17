import rclpy
from rclpy.node import Node
from yolo_msgs.msg import DetectionArray, Detection
from irobot_create_msgs.msg import AudioNoteVector, AudioNote
from builtin_interfaces.msg import Duration

class DetectionChime(Node):
    def __init__(self):

        super().__init__('detection_chime_node')

        self.NUMBER_OF_CHIMES = 0               # How many times has the robot screamed
        self.MAX_CHIMES = 1                     # After how many screams should it stop screaming

        self.detect_subscriber = self.create_subscription(DetectionArray, '/yolo/detections', self.callback, 10)
        self.detect_subscriber

        self.sound_pub = self.create_publisher(AudioNoteVector, '/robot4/cmd_audio', 10)

    def callback(self, msg):
        human_detected = False
        audio_msg = AudioNoteVector()
        for detection in msg.detections:
            if detection.class_name == 'person' and detection.score > 0.6:
                self.get_logger().info("Human detected")
                if self.NUMBER_OF_CHIMES < self.MAX_CHIMES:
                    audio_msg = self.chime(audio_msg)
                self.NUMBER_OF_CHIMES += 1
                break
        audio_msg.append = True
        self.sound_pub.publish(audio_msg)
    
    def chime(self, msg):
        Melody = [1976, 1568, 1760, 2093]

        for freq in Melody:
            note = AudioNote()           
            time_play = Duration()
 
            time_play.nanosec = 150000000 # 0.15 seconds
            note.max_runtime = time_play
            note.frequency = freq

            msg.append = True
            msg.notes.append(note)

        return msg

def main(args=None):
    rclpy.init(args=args)
    
    node = DetectionChime()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()