import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from yolo_msgs.msg import HallwayAck
from irobot_create_msgs.msg import AudioNote, AudioNoteVector
from builtin_interfaces.msg import Duration
from std_msgs.msg import String
import time

class DodgeNode(Node):
    # phases
    STRAIGHT = 0
    ARC_RIGHT = 1
    ARC_LEFT = 2

    def __init__(self):
        super().__init__('dodge_node')

        self.SOUNDS = True                         # do we want sounds
        self.LIGHTS = True                          # do we want lights

        self.LEFT_LIGHTS = "turn 1 500"             # light state when dodging
        self.RIGHT_LIGHTS = "turn 0 500"            # light state when dodging
        self.DEFAULT_LIGHT_STATE = "instant 85 1"    # default light state when not dodging

        self.FORWARD_SPD = 0.5          # m/s
        self.TURN_RATE = 0.5            # rad/s
        self.ARC_DURATION = 2.0         # s, time spent in EACH arc

        self.CONF_THRESH = 0.0          # min confidence
        self.TRIGGER_HEIGHT = 70        # bbox_height that starts the dodge

        self.phase = self.STRAIGHT
        self.dodge_timer = None
        self.HAS_SEEN = False
        self.HAS_RETURNED = False

        # pubs and subs
        self.publisher = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)
        self.ack_sub = self.create_subscription(HallwayAck, '/robot4/hallway_ack', self.hallway_cb, 10)
        self.sound_pub = self.create_publisher(AudioNoteVector, "/robot4/cmd_audio", 2)
        self.light_pub = self.create_publisher(String, "/light_state", 10)
        
        self.timer = self.create_timer(0.1, self.control_loop)

    def hallway_cb(self, msg):
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

            if self.SOUNDS:
                self.change_sounds()

            self.get_logger().info("Person detected -- arcing right.")
            self.phase = self.ARC_RIGHT
            self.dodge_timer = self.create_timer(self.ARC_DURATION, self.begin_left)
        
        if (self.HAS_SEEN 
            and not self.HAS_RETURNED
            and not msg.person_detected
            and self.phase == self.STRAIGHT):
            self.HAS_RETURNED = True

            if self.SOUNDS:
                self.change_sounds_again()

            self.get_logger().info("Person no longer detected -- arcing left.")
            self.phase = self.ARC_LEFT
            self.dodge_timer = self.create_timer(self.ARC_DURATION, self.begin_right)

    # ================================================================================
    # LIGHTS
    # ================================================================================
    def change_light_state(self):
        # change light state to...
        light_msg = String()
        if self.phase == self.ARC_RIGHT:
            light_msg.data = self.RIGHT_LIGHTS

        elif self.phase == self.ARC_LEFT:
            light_msg.data = self.LEFT_LIGHTS

        elif self.phase == self.STRAIGHT:
            light_msg.data = self.DEFAULT_LIGHT_STATE
        
        self.light_pub.publish(light_msg)
    
    # ================================================================================
    # SOUNDS
    # ================================================================================
    def change_sounds(self):
        audio_msg = AudioNoteVector()
        Melody = [1174, 1318, 1568]
        Durations = [.2, .2, .4]
        for x in range(len(Melody)):
            note = AudioNote()           
            time_play = Duration()

            time_play.nanosec = int(Durations[x] * 1000000000) # val * 1 second
            note.max_runtime = time_play
            note.frequency = Melody[x]

            audio_msg.append = True
            audio_msg.notes.append(note)

        self.sound_pub.publish(audio_msg)

    def change_sounds_again(self):
        audio_msg = AudioNoteVector()
        Melody = [1568, 1318, 1174]
        Durations = [.2, .2, .4]
        for x in range(len(Melody)):
            note = AudioNote()           
            time_play = Duration()

            time_play.nanosec = int(Durations[x] * 1000000000) # val * 1 second
            note.max_runtime = time_play
            note.frequency = Melody[x]

            audio_msg.append = True
            audio_msg.notes.append(note)

        self.sound_pub.publish(audio_msg)

    # ================================================================================
    # MOVEMENT
    # ================================================================================
    def begin_left(self):
        # right arc done; now arc back left by the same amount to straighten out
        self.get_logger().info("Arcing back left.")
        self.phase = self.ARC_LEFT
        if self.LIGHTS:
            self.change_light_state()
        self._reset_timer(self.finish_dodge, self.ARC_DURATION)
    
    def begin_right(self):
        # left arc done; now arc back right by the same amount to straighten out
        self.get_logger().info("Arcing back right.")
        self.phase = self.ARC_RIGHT
        if self.LIGHTS:
            self.change_light_state()
        self._reset_timer(self.finish_dodge, self.ARC_DURATION)


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