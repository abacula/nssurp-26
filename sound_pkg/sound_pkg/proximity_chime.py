import rclpy
from rclpy.node import Node
from yolo_msgs.msg import DetectionArray
from irobot_create_msgs.msg import AudioNoteVector, AudioNote
from builtin_interfaces.msg import Duration

class ProximityAcknowledge(Node):
    def __init__(self):
        super().__init__('proximity_acknowledge_node')

        # to prevent constant screaming
        self.has_acknowledged = False 
        
        # bh=68 is ~30ft away
        self.ACTIVATION_THRESHOLD_BH = 68 

        self.detect_subscriber = self.create_subscription(DetectionArray, '/yolo/detections', self.callback, 10)

        self.sound_pub = self.create_publisher(AudioNoteVector, '/robot4/cmd_audio', 10)

    def callback(self, msg):
        for detection in msg.detections:
            if detection.class_name == 'person' and detection.score > 0.85:
                
                current_bh = detection.bbox.size.y 
                
                if current_bh >= self.ACTIVATION_THRESHOLD_BH and not self.has_acknowledged:
                    self.get_logger().info(f"Human acknowledged at bh: {current_bh}")
                    self.trigger_greeting()
                    self.has_acknowledged = True
                
                # reset logic
                elif current_bh < (self.ACTIVATION_THRESHOLD_BH - 10):
                    self.has_acknowledged = False

    def trigger_greeting(self):
        audio_msg = AudioNoteVector()
        audio_msg.append = True
        
        for freq in range(600, 1400, 50):
            note = AudioNote()
            time_play = Duration()
            
            time_play.nanosec = 20000000 
            note.max_runtime = time_play
            note.frequency = freq
            
            audio_msg.notes.append(note)

        self.sound_pub.publish(audio_msg)

def main(args=None):
    rclpy.init(args=args)
    node = ProximityAcknowledge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()