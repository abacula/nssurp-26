import rclpy
from rclpy.node import Node
from yolo_msgs.msg import HallwayAck
from irobot_create_msgs.msg import LightringLeds, AudioNote, AudioNoteVector
from builtin_interfaces.msg import Duration

# Any additional imports here

# Decide your node class name
class behaviorTest(Node):
    def __init__(self):

        # Change to have your node name
        super().__init__('behavior_test_node')
        self.has_seen = False

        self.acknowledgement_sub = self.create_subscription(HallwayAck, '/robot4/hallway_ack', self.behavior_cb, 10)

        self.sound_pub = self.create_publisher(AudioNoteVector, "/robot4/cmd_audio", 2)
        self.light_pub = self.create_publisher(LightringLeds, "/robot4/cmd_lightring", 10)

    def behavior_cb(self, msg):
        if msg.person_detected and msg.confidence >= 0.75:
            if msg.bbox_height > 90:
                self.changeLEDS(100,0,100)
                self.changeSound(True)
                self.has_seen = True
            else:
                self.changeLEDS(0,0,0)
                self.changeSound(False)
            
        else:
                self.changeLEDS(0,0,0)
                self.changeSound(False)
                self.has_seen = False
    
    def changeLEDS(self, r, g ,b):
        light_msg = LightringLeds()
        light_msg.override_system = True
        for i in range(6):
            light_msg.leds[i].red = r
            light_msg.leds[i].green = g
            light_msg.leds[i].blue = b
        self.light_pub.publish(light_msg)

    def changeSound(self, on):
        if on and not self.has_seen:
            audio_msg = AudioNoteVector()
            Melody = [1976, 1568, 1760, 2093]
            for freq in Melody:
                note = AudioNote()           
                time_play = Duration()
    
                time_play.nanosec = 150000000 # 0.15 seconds
                note.max_runtime = time_play
                note.frequency = freq

                audio_msg.append = True
                audio_msg.notes.append(note)
            self.sound_pub.publish(audio_msg)
        else:
            audio_msg = AudioNoteVector()
            audio_msg.append = True
            self.sound_pub.publish(audio_msg)



def main(args=None):
    rclpy.init(args=args)

    # Change to be your node class name
    node = behaviorTest()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()