import sys
import threading
import termios
import tty
import select
import pynput
import rclpy
from rclpy.node import Node
from arm_ctrl_msgs.msg import Arm
import time

KEY_BINDINGS = {
    'w': ('link1',  1),
    's': ('link1', -1),
    'e': ('link2',  1),
    'd': ('link2', -1),
    'r': ('link3',  1),
    'f': ('link3', -1),
    ",": ('base',  1),
    ".": ('base', -1),
    "i": ('servo_dir',  (1, 1)),
    "k": ('servo_dir',  (-1, -1)),
    "j": ('servo_dir',  (-1, 1)),
    "l": ('servo_dir',  (1, -1)),
    "u": ('tool', 1),
    "o": ('tool', 0),
    " ": ("stop", None),
    "q": ("quit", None),
}


class ArmTeleop(Node):
    def __init__(self):
        super().__init__('arm_teleop')
        self.pub = self.create_publisher(Arm, 'arm_cmd', 10)
        self.get_logger().info("Use w/s, e/d, r/f to control link1, link2, link3, ,/. for base rotation, i/k/j/l for servo directions, u/o for tool, space to stop.")
        self.arm = Arm()
        self._stop_event = threading.Event()
        self._timer = self.create_timer(0.1, self.timer_callback)
        self.listener = pynput.keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        self._start_stdin_listener()

    def _start_stdin_listener(self):
        if not sys.stdin.isatty():
            self.get_logger().warn("STDIN is not a TTY; keyboard fallback disabled.")
            return

        self._stdin_thread = threading.Thread(target=self._stdin_listener, daemon=True)
        self._stdin_thread.start()

    def _stdin_listener(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while not self._stop_event.is_set():
                rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
                if rlist:
                    char = sys.stdin.read(1)
                    self.handle_char(char, source="stdin")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def handle_char(self, char, source=""):
        if char == '\x03':  # Ctrl+C in raw stdin
            char = 'q'
        if char in KEY_BINDINGS:
            command = KEY_BINDINGS[char]
            if command[0] == 'stop':
                self.arm = Arm()  # Reset all commands
            elif command[0] == 'quit':
                self.get_logger().info("Quit requested.")
                rclpy.shutdown()
                return
            elif command[0] == 'servo_dir':
                self.arm.servo1_dir = command[1][0]
                self.arm.servo2_dir = command[1][1]
            else:
                current_value = getattr(self.arm, command[0])
                new_value = current_value + command[1]
                if new_value > 1:
                    new_value = 1
                elif new_value < -1:
                    new_value = -1
                setattr(self.arm, command[0], new_value)

            self.get_logger().info(
                f"Key pressed: {repr(char)} ({source or 'pynput'}), updated arm command: {self.arm}"
            )
    def on_press(self, key):
        try:
            try:
                char = key.char
            except AttributeError:
                # Handle special keys like space
                if key == pynput.keyboard.Key.space:
                    char = ' '
                else:
                    return

            self.handle_char(char, source="pynput")
        except Exception as e:
            self.get_logger().error(f"Error in on_press: {e}")

    def timer_callback(self):
        self.pub.publish(self.arm)

    def destroy_node(self):
        self._stop_event.set()
        return super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    interface = ArmTeleop()
    try:
        rclpy.spin(interface)
    except KeyboardInterrupt:
        pass
    interface.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()