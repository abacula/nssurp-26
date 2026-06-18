import rclpy
import time
from rclpy.node import Node
from yolo_msgs.msg import HallwayAck
from geometry_msgs.msg import Twist
from irobot_create_msgs.msg import AudioNote, AudioNoteVector
from builtin_interfaces.msg import Duration

# Any additional imports here

# Decide your node class name
class LiaSound(Node):
    def __init__(self):

        self.can_play = True

        # Change to have your node name
        super().__init__('lia_sound_node')

        self.sound_pub = self.create_publisher(AudioNoteVector, "/robot4/cmd_audio", 2)

        self.timer = self.create_timer(0.1, self.loop)

    def loop(self):
        
        if self.can_play:
            self.changeSound(True)
        else:
            self.changeSound(False)

    def changeSound(self, on):

        if on:
            self.can_play = False
            
            audio_msg = AudioNoteVector()
            #Melody = [1174, 1318, 1568, 1174]
            #Durations = [.2, .2, .4, .2]
            #Melody = [1396, 1318, 1396, 1318]
            #Durations = [.2, .2, .2, .2]
            Melody = [1318, 1568, 1760, 1396]
            Durations = [.2, .2, .2, .2]
            #Melody = [1318, 1568, 1760, 1568, 1396]
            #Durations = [.2, .2, .2, .2, .2]
            #Melody = [0.0]
            #Durations = [0]
            for x in range(len(Melody)):
                note = AudioNote()           
                time_play = Duration()
    
                time_play.nanosec = int(Durations[x] * 1000000000) # val * 1 second
                note.max_runtime = time_play
                note.frequency = Melody[x]

                audio_msg.append = True
                audio_msg.notes.append(note)
            self.sound_pub.publish(audio_msg)

            time.sleep(sum(Durations) * 2.0)
            self.can_play = True
        else:
            audio_msg = AudioNoteVector()
            audio_msg.append = True
            self.sound_pub.publish(audio_msg)


def main(args=None):
    rclpy.init(args=args)

    # Change to be your node class name
    node = LiaSound()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()