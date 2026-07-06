import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
from geometry_msgs.msg import Twist
from yolo_msgs.msg import HallwayAck
from irobot_create_msgs.msg import AudioNote, AudioNoteVector
from builtin_interfaces.msg import Duration
from std_msgs.msg import String
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
import time

class DodgeNode(Node):
    # phases
    STRAIGHT = 0
    ARC_RIGHT = 1
    ARC_LEFT = 2

    def __init__(self):
        super().__init__('dodge_node')

        self.SOUNDS = False                           # do we want sounds
        self.LIGHTS = False                           # do we want lights

        self.DODGE_LIGHTS = "fade 5 42 5"            # light state when dodging
        self.DEFAULT_LIGHT_STATE = "instant 85 1"    # default light state when not dodging

        self.FORWARD_SPD = 0.5          # m/s
        self.TURN_RATE = 0.45            # rad/s
        self.ARC_DURATION = 2.5         # s, time spent in EACH arc

        self.CONF_THRESH = 0.0          # min confidence
        self.TRIGGER_HEIGHT = 70        # bbox_height that starts the dodge
        self.OBSTACLE_DETECTED = False  # stop movement if obstacle detected
        self.OBS_THRESH = 0.5           # m, distance to obstacle that triggers stop

        self.control_callback_group = MutuallyExclusiveCallbackGroup()
        self.dodge_callback_group = MutuallyExclusiveCallbackGroup()

        self.phase = self.STRAIGHT
        self.dodge_timer = None
        self.HAS_SEEN = False
        self.HAS_RETURNED = False

        # pubs and subs
        self.ack_sub = self.create_subscription(HallwayAck, '/robot4/hallway_ack', self.hallway_cb, 10)
        self.scan_sub = self.create_subscription(LaserScan, '/robot4/scan', self.scan_cb, 10)

        self.publisher = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)
        self.sound_pub = self.create_publisher(AudioNoteVector, "/robot4/cmd_audio", 2)
        self.light_pub = self.create_publisher(String, "/light_state", 10)
        
        self.timer = self.create_timer(0.1, self.control_loop, callback_group=self.control_callback_group)

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
            self.dodge_timer = self.create_timer(self.ARC_DURATION, self.begin_left, callback_group=self.dodge_callback_group)
        
        if (self.HAS_SEEN 
            and not self.HAS_RETURNED
            and not msg.person_detected
            and self.phase == self.STRAIGHT):
            self.HAS_RETURNED = True

            # if self.SOUNDS:
                # self.change_sounds_again()

            self.get_logger().info("Person no longer detected -- arcing left.")
            self.phase = self.ARC_LEFT
            self.dodge_timer = self.create_timer(self.ARC_DURATION, self.begin_right, callback_group=self.dodge_callback_group)
    
    def scan_cb(self, msg):
        front_ranges = msg.ranges[200:340]
        min = msg.range_min
        max = msg.range_max
        for distance in front_ranges:
            if distance <= min or distance >= max:
                continue

            if distance < self.OBS_THRESH:
                self.OBSTACLE_DETECTED = True
                self.get_logger().warn("Obstacle detected -- stopping movement.")
                break
            else:
                self.OBSTACLE_DETECTED = False

    # ================================================================================
    # LIGHTS
    # ================================================================================
    def change_light_state(self):
        # change light state to...
        light_msg = String()
        if self.phase != self.STRAIGHT:
            light_msg.data = self.DODGE_LIGHTS

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

    # for testing purposes, play the reversed melody when the person is no longer detected
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
        self._reset_timer(self.finish_dodge, self.ARC_DURATION)
    
    def begin_right(self):
        # left arc done; now arc back right by the same amount to straighten out
        self.get_logger().info("Arcing back right.")
        self.phase = self.ARC_RIGHT
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
            self.dodge_timer = self.create_timer(duration, next_cb, callback_group=self.dodge_callback_group)

    def control_loop(self):
        twist = Twist()
        twist.linear.x = self.FORWARD_SPD       # always rolling forward
        if self.phase == self.ARC_RIGHT:
            twist.angular.z = -self.TURN_RATE   # curve right, around the person
        elif self.phase == self.ARC_LEFT:
            twist.angular.z = self.TURN_RATE    # equal/opposite curve back to original heading
        else:
            twist.angular.z = 0.0               # straight down the hallway

        if self.OBSTACLE_DETECTED:
            twist.linear.x = 0.0
            twist.angular.z = 0.0

        self.publisher.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = DodgeNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()