import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from irobot_create_msgs.msg import AudioNoteVector, AudioNote
from builtin_interfaces.msg import Duration

class BatteryAlarm(Node):
    def __init__(self):

        super().__init__('battery_alarm_node')

        self.LOW_BATTERY_THRESHOLD = 0.21        # What battery percentage should it start screaming
        self.NUMBER_OF_CHIMES = 0               # How many times has the robot screamed
        self.MAX_CHIMES = 2                     # After how many screams should it stop screaming
        self.DONE_TALKING = False               # Is the robot done screaming

        self.battery_subscriber = self.create_subscription(BatteryState, '/robot4/battery_state', self.callback, 10)
        self.battery_subscriber

        self.sound_pub = self.create_publisher(AudioNoteVector, '/robot4/cmd_audio', 10)

    def callback(self, msg):
        battery_percentage = msg.percentage
        audio_msg = self.play_audio(battery_percentage)
        self.sound_pub.publish(audio_msg)

    def play_audio(self, percentage):
        audio_msg = AudioNoteVector()
        if (percentage < self.LOW_BATTERY_THRESHOLD and self.NUMBER_OF_CHIMES < self.MAX_CHIMES):
            audio_msg = self.alarm(audio_msg)
            self.NUMBER_OF_CHIMES += 1
        return audio_msg
    
    def alarm(self, msg):
        Melody = [932, 784, 880, 698]

        for freq in Melody:
            note = AudioNote()
            
            time_play = Duration()
            # time_play.sec = 
            time_play.nanosec = 400000000 # 0.4 seconds
            note.max_runtime = time_play

            note.frequency = freq
            msg.notes.append(note)

        return msg

def main(args=None):
    rclpy.init(args=args)
    
    node = BatteryAlarm()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()