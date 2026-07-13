import rclpy
import time
from rclpy.node import Node
from yolo_msgs.msg import HallwayAck
from geometry_msgs.msg import Twist
from irobot_create_msgs.msg import AudioNote, AudioNoteVector
from builtin_interfaces.msg import Duration
from std_msgs.msg import String
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from tf_transformations import euler_from_quaternion

class WaveMLS(Node):
    def __init__(self):
        super().__init__('w_mls')

        self.LIGHTS = True                    # do we want lights
        self.INITIAL_LIGHT_STATE = True       # do we want lights to be set to initial state
        self.SOUNDS = True                     # do we want sounds

        self.SPEED = 0.5                # m/s
        self.CONF_THRESH = 0.75         # min confidence
        self.TRIGGER_HEIGHT = 70        # bbox_height that starts the wave

        self.PERSON_DETECTED = False
        self.OBSTACLE_DETECTED = False              # stop movement if obstacle detected
        self.OBS_THRESH = 0.75                       # m, distance to obstacle that triggers stop
        
        self.ANG_THRESH = 0.02                       # rad, angle that triggers stop
        self.PI = 3.141592653589793
        self.ANG = 0
        self.ANG_OFFSET = 0
        self.GOT_OFFSET = False

        self.WAVING = False
        self.WAVED = False

        # subs and pubs
        self.publisher = self.create_publisher(Twist, '/robot4/cmd_vel_unstamped', 10)
        self.sound_pub = self.create_publisher(AudioNoteVector, "/robot4/cmd_audio", 2)
        self.ack_sub = self.create_subscription(HallwayAck, '/robot4/hallway_ack', self.hallway_cb, 10)
        self.light_pub = self.create_publisher(String, "/light_state", 10)
        self.scan_sub = self.create_subscription(LaserScan, '/robot4/scan', self.scan_cb, 10)
        self.odom_sub = self.create_subscription(Odometry, '/robot4/odom', self.odom_cb, 10)


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

    def scan_cb(self, msg):
        self.OBSTACLE_DETECTED = False
        front_ranges = msg.ranges[200:340]
        min = msg.range_min
        max = msg.range_max
        for distance in front_ranges:
            if distance > min or distance < max:
                if distance < self.OBS_THRESH:
                    self.OBSTACLE_DETECTED = True
                    self.get_logger().warn("Obstacle detected -- stopping movement.")
                    

    def odom_cb(self, msg):
        quaternion = msg.pose.pose.orientation
         # Angle converted from quaternion to euler
        (_,_,ang) = euler_from_quaternion([quaternion.x, quaternion.y, quaternion.z, quaternion.w])

        if self.GOT_OFFSET is False:
            self.ANG_OFFSET = -ang
            self.GOT_OFFSET = True

        ang += self.ANG_OFFSET
        
        if ang < -self.PI:
            self.ANG = ang + (2*self.PI)
        else:
            self.ANG = ang

    # ================================================================================
    # LIGHTS
    # ================================================================================
    def change_light_state(self):
        light_msg = String()
        if self.WAVING:
            light_msg.data = "fade 5 42 5"
        else:
            light_msg.data = "instant 85 1"

        self.light_pub.publish(light_msg)

    # ================================================================================
    # SOUNDS
    # ================================================================================
    def changeSound(self):
        if self.SOUNDS:
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

        # done waving, reset state
        self.WAVING = False
        self.change_light_state()


    def loop(self):
        twist = Twist()
        twist.linear.x = self.SPEED
        if self.PERSON_DETECTED or self.WAVING or self.OBSTACLE_DETECTED or self.GOT_OFFSET is False:
            twist.linear.x = 0.0
        else:
            if self.ANG > self.ANG_THRESH:
                twist.angular.z = -0.15
                self.get_logger().info("Turning right to correct orientation.")
            elif self.ANG < -self.ANG_THRESH:
                twist.angular.z = 0.15
                self.get_logger().info("Turning left to correct orientation.")
            else:
                self.get_logger().info(str(round(self.ANG,3)))

        self.publisher.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = WaveMLS()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()