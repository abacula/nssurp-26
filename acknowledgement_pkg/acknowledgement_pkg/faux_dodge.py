import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from yolo_msgs.msg import HallwayAck
from irobot_create_msgs.msg import AudioNote, AudioNoteVector
from builtin_interfaces.msg import Duration
from std_msgs.msg import String

class DodgeNode(Node):
    # phases
    STRAIGHT = 0
    ARC_RIGHT = 1
    ARC_LEFT = 2

    def __init__(self):
        super().__init__('dodge_node')

        self.SOUNDS = False                         # do we want sounds
        self.LIGHTS = True                          # do we want lights (not implemented yet)

        self.LIGHT_STATE = "fade 5 171"             # light state when dodging 
        self.DEFAULT_LIGHT_STATE = "instant 171"    # default light state when not dodging

        self.FORWARD_SPD = 0.5          # m/s
        self.TURN_RATE = 0.5            # rad/s
        self.ARC_DURATION = 2.5         # s, time spent in EACH arc

        self.CONF_THRESH = 0.70
        self.TRIGGER_HEIGHT = 74        # bbox_height that starts the dodge

        self.phase = self.STRAIGHT
        self.dodge_timer = None
        self.HAS_SEEN = False

        # pubs and subs
        self.publisher = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)
        self.ack_sub = self.create_subscription(HallwayAck, '/robot4/hallway_ack', self.hallway_cb, 10)
        self.sound_pub = self.create_publisher(AudioNoteVector, "/robot4/cmd_audio", 2)
        self.light_pub = self.create_publisher(String, "/light_state", 10)
        
        self.timer = self.create_timer(0.1, self.control_loop)

    def hallway_cb(self, msg):
        if self.SOUNDS:
            self.change_sounds()
        if self.LIGHTS:
            self.change_light_state()

        # ignore detections once a dodge is already underway
        if self.phase != self.STRAIGHT:
            return

        if (msg.person_detected
                and msg.confidence >= self.CONF_THRESH
                and msg.bbox_height > self.TRIGGER_HEIGHT
                and not self.HAS_SEEN):
            self.HAS_SEEN = True
            self.get_logger().info("Person detected -- arcing right.")
            self.phase = self.ARC_RIGHT
            self.dodge_timer = self.create_timer(self.ARC_DURATION, self.begin_left)

    # ================================================================================
    # LIGHTS
    # ================================================================================
    def change_light_state(self):
        # change light state to pulse while dodging, and turn off when done or otherwise
        if self.phase != self.STRAIGHT:
            light_msg = String()
            light_msg.data = self.LIGHT_STATE
            self.light_pub.publish(light_msg)

        elif self.phase == self.STRAIGHT:
            light_msg = String()
            light_msg.data = self.DEFAULT_LIGHT_STATE
            self.light_pub.publish(light_msg)
    
    # ================================================================================
    # SOUNDS
    # ================================================================================
    def change_sounds(self):
        # play sound while dodging, and stop when done or otherwise
        if self.phase != self.STRAIGHT:
            audio_msg = AudioNoteVector()
            Melody = [880,698]
            for freq in Melody:
                note = AudioNote()           
                time_play = Duration()

                time_play.nanosec = 1000000000 # 1 second(s)
                note.max_runtime = time_play
                note.frequency = freq

                audio_msg.append = True
                audio_msg.notes.append(note)
            self.sound_pub.publish(audio_msg)
            
        elif self.phase != self.STRAIGHT:
            audio_msg = AudioNoteVector()
            audio_msg.append = False
            self.sound_pub.publish(audio_msg)
            self.get_logger().info("Sound Killed.")

    # ================================================================================
    # MOVEMENT
    # ================================================================================
    def begin_left(self):
        # right arc done; now arc back left by the same amount to straighten out
        self.get_logger().info("Arcing back left.")
        self.phase = self.ARC_LEFT
        self._reset_timer(self.finish_dodge, 1.25 * self.ARC_DURATION)

    def finish_dodge(self):
        self.get_logger().info("Dodge complete -- driving straight down the hallway.")
        self.phase = self.STRAIGHT
        self._reset_timer(None)

    def _reset_timer(self, next_cb, duration=None):
        if self.dodge_timer is not None:
            self.dodge_timer.cancel()
            self.dodge_timer = None
        if next_cb is not None:
            self.dodge_timer = self.create_timer(duration, next_cb)

    def control_loop(self):
        twist = Twist()
        twist.linear.x = self.FORWARD_SPD       # always rolling forward

        if self.phase == self.ARC_RIGHT:
            twist.angular.z = -self.TURN_RATE   # curve right, around the person
        elif self.phase == self.ARC_LEFT:
            twist.angular.z = self.TURN_RATE    # equal/opposite curve back to original heading
        else:
            twist.angular.z = 0.0               # straight down the hallway

        self.publisher.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = DodgeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()