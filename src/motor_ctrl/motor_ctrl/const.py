import rclpy
from rclpy.node import Node
import serial
from geometry_msgs.msg import Twist

class MotorInterface(Node):
    def __init__(self):
        super().__init__("motor_interface")
        self.declare_parameter("port", "/dev/ttyACM0")
        self.declare_parameter("baudrate", 115200)
        self.declare_parameter("command_speed", 500)

        port = self.get_parameter("port").value
        baudrate = self.get_parameter("baudrate").value
        self.command_speed = int(self.get_parameter("command_speed").value)

        try:
            self.serial = serial.Serial(port, baudrate=baudrate, timeout=1)
        except serial.SerialException as exc:
            self.serial = None
            self.get_logger().error(f"Failed to open {port}: {exc}")

        self.subscriber = self.create_subscription(Twist, topic='cmd_vel', callback=self.cmd_vel_callback, qos_profile=10)
        self.array = [0.0, 0.0]
        self.wheel_rad = 0.105
        self.wheel_sep = 0.95
        self.create_rate(1)

    def cmd_vel_callback(self, msg):
        if self.serial is None or not self.serial.is_open:
            return

        angular = msg.angular.z
        linear = msg.linear.x
        self.w_r = (linear / self.wheel_rad) + ((angular * self.wheel_sep) / (2.0 * self.wheel_rad))
        self.w_l = (linear / self.wheel_rad) - ((angular * self.wheel_sep) / (2.0 * self.wheel_rad))

        out_r = self.command_speed if self.w_r > 0 else -self.command_speed if self.w_r < 0 else 0
        out_l = self.command_speed if self.w_l > 0 else -self.command_speed if self.w_l < 0 else 0

        data = f"{out_l},{out_r}\n"
        self.serial.write(data.encode())

def main(args = None):
    rclpy.init(args=args)
    interface = MotorInterface()
    rclpy.spin(interface)
    interface.destroy_node()
    rclpy.shutdown()

if __name__=="__main__":
    main()