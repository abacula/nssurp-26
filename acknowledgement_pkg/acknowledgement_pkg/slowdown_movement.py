import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from yolo_msgs.msg import HallwayAck
from irobot_create_msgs.msg import AudioNote, AudioNoteVector
from builtin_interfaces.msg import Duration
from std_msgs.msg import String


class SlowdownMovement(Node):
    def __init__(self):
        super().__init__('slowdown_node')

        self.SOUND = True               # do we want sounds
        self.LIGHTS = True              # do we want lights (not implemented yet)
        self.FADE_RATE = 5
        self.FORWARD_SPD = 0.5          # m/s
        self.CONF_THRESH = 0.75         # min confidence
        self.TRIGGER_HEIGHT = 70        # bbox_height that starts the slowdown

        self.publisher = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)
        self.ack_sub = self.create_subscription(HallwayAck, '/robot4/hallway_ack', self.hallway_cb, 10)
        self.sound_pub = self.create_publisher(AudioNoteVector, "/robot4/cmd_audio", 2)
        self.light_pub = self.create_publisher(String, "/light_state", 10)

    def hallway_cb(self, msg):
        twist = Twist()
        if (msg.person_detected
                and msg.confidence >= self.CONF_THRESH
                and msg.bbox_height > self.TRIGGER_HEIGHT):
            self.get_logger().info("Person detected -- slowing down.")
            twist.linear.x = self.get_speed(msg.bbox_height)
            if msg.bbox_height > 230:
                twist.linear.x = 0.0

        else:
            self.get_logger().info("No person detected -- keep moving.")
            twist.linear.x = self.FORWARD_SPD

        if self.SOUND and twist.linear.x < self.FORWARD_SPD:
            audio_msg = AudioNoteVector()
            Melody = [880,698]
            for freq in Melody:
                note = AudioNote()           
                time_play = Duration()
    
                # time_play.nanosec = 1000000000 # 1 seconds
                time_play.sec = 1
                note.max_runtime = time_play
                note.frequency = freq

                audio_msg.append = True
                audio_msg.notes.append(note)
                
        else:
            audio_msg = AudioNoteVector()
            audio_msg.append = False
           
        if self.LIGHTS:
            light_msg = String()
            if twist.linear.x == 0:
                light_msg.data = "instant 0"
            elif twist.linear.x < self.FORWARD_SPD:
                light_msg.data =  f'fade {self.FADE_RATE} 42'

            else:
                light_msg.data = "instant 85"
        self.light_pub.publish(light_msg)    
        self.sound_pub.publish(audio_msg)
        self.publisher.publish(twist)

    def get_speed(self, box_height, max_speed = 0.5, min_speed=0.05):
        ratio = (self.TRIGGER_HEIGHT) / (box_height*1.35)                   # 0.0 (close) to 1.0 (far)
        return float(min_speed + ratio * (max_speed - min_speed))

def main(args=None):
    rclpy.init(args=args)
    node = SlowdownMovement()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()