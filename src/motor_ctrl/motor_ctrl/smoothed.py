import rclpy
from rclpy.node import Node
import serial
from geometry_msgs.msg import Twist

class MotorInterface(Node):
    def __init__(self):
        super().__init__("motor_interface")
        self.serial = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=1)
        self.subscriber = self.create_subscription(Twist, topic='cmd_vel_smoothed', callback=self.cmd_vel_callback, qos_profile=10)
        self.array = [0.0, 0.0]
        self.wheel_rad = 0.0125
        self.wheel_sep = 0.600
        self.create_rate(1)

    def cmd_vel_callback(self, msg):
        angular = msg.angular.z
        linear = msg.linear.x
        self.w_r = (linear / self.wheel_rad) + ((angular * self.wheel_sep) / (2.0 * self.wheel_rad))
        self.w_r = max(-255, self.w_r) if self.w_r < 0 else min(255, self.w_r)
        self.w_l = (linear / self.wheel_rad) - ((angular * self.wheel_sep) / (2.0 * self.wheel_rad))
        self.w_l = max(-255, self.w_l) if self.w_l < 0 else min(255, self.w_l)
        self.get_logger().info(f"Right Wheel Velocity: {self.w_r}, Left Wheel Velocity: {self.w_l}")
        data = f"{int(self.w_r)},{int(-self.w_l)}\n"
        self.serial.write(data.encode())

def main(args = None):
    rclpy.init(args=args)
    interface = MotorInterface()
    rclpy.spin(interface)
    interface.destroy_node()
    rclpy.shutdown()

if __name__=="__main__":
    main()
