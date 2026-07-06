import rclpy
import time
from rclpy.node import Node
from yolo_msgs.msg import HallwayAck
from geometry_msgs.msg import Twist
from irobot_create_msgs.msg import AudioNote, AudioNoteVector
from builtin_interfaces.msg import Duration
from std_msgs.msg import String

class Wave(Node):
    def __init__(self):

        self.person_detected = False
        self.speed = 0.5
        self.waving = False
        self.waved = False
        self.lights = False
        self.sound = False

        # Change to have your node name
        super().__init__('wave_node')

        self.LIGHTS = False                     # do we want lights
        self.INITIAL_LIGHT_STATE = False        # do we want lights to be set to initial state
        self.SOUNDS = False                     # do we want sounds

        self.SPEED = 0.5                # m/s
        self.CONF_THRESH = 0.75         # min confidence
        self.TRIGGER_HEIGHT = 70        # bbox_height that starts the wave

        self.PERSON_DETECTED = False

        self.WAVING = False
        self.WAVED = False

        # subs and pubs
        self.publisher = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)
        self.sound_pub = self.create_publisher(AudioNoteVector, "/robot4/cmd_audio", 2)
        self.ack_sub = self.create_subscription(HallwayAck, '/robot4/hallway_ack', self.hallway_cb, 10)
        self.light_pub = self.create_publisher(String, "/light_state", 10)

        self.timer = self.create_timer(0.1, self.loop)
    
    def hallway_cb(self, msg):
        if self.LIGHTS and self.INITIAL_LIGHT_STATE:
            self.INITIAL_LIGHT_STATE = False
            self.change_light_state()
            
        if (msg.person_detected 
            and msg.bbox_height > self.TRIGGER_HEIGHT 
            and not self.WAVED):

            self.PERSON_DETECTED = True
            self.wave()

        else:
            self.PERSON_DETECTED = False

    # ================================================================================
    # LIGHTS
    # ================================================================================
    def change_light_state(self):
        light_msg = String()
        if self.WAVING:
            light_msg.data = "rainbow 10"
        else:
            light_msg.data = "instant 85 1"

        self.light_pub.publish(light_msg)

    # ================================================================================
    # SOUNDS
    # ================================================================================
    def changeSound(self):
        
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

        if self.sound:
            self.sound_pub.publish(audio_msg)

    # ================================================================================
    # MOVEMENT
    # ================================================================================
    def wave(self):

        # start waving, set state
        self.WAVING = True
        self.WAVED = True
        self.change_light_state()

        twist = Twist()
        twist.linear.x = 0.0
        
        # Turn left
        twist.angular.z = 1.0
        self.publisher.publish(twist)
        time.sleep(0.5)
        
        twist.angular.z = 0.0
        self.publisher.publish(twist)
        self.changeSound()

        # Wave left
        twist.angular.z = 0.5
        self.publisher.publish(twist)
        time.sleep(0.5)
        
        # Wave right
        twist.angular.z = -0.5
        self.publisher.publish(twist)
        time.sleep(0.5)
        twist.angular.z = -0.5
        self.publisher.publish(twist)
        time.sleep(0.5)

        # Return left
        twist.angular.z = 0.5
        self.publisher.publish(twist)
        time.sleep(0.5)

        # Turn right
        twist.angular.z = -0.5
        self.publisher.publish(twist)
        time.sleep(0.5)
        
        twist.angular.z = 0.0
        self.publisher.publish(twist)

        time.sleep(0.5)
        self.waving = False

    def loop(self):
        twist = Twist()
        twist.linear.x = 0.5
        if self.PERSON_DETECTED or self.WAVING:
            twist.linear.x = 0.0

        self.publisher.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = Wave()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()