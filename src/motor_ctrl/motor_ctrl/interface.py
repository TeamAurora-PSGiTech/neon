import rclpy
from rclpy.node import Node
import serial
from geometry_msgs.msg import Twist


class MotorInterface(Node):
    def __init__(self):
        super().__init__("motor_interface")

        # Declare configurable parameters
        self.declare_parameter("port", "/dev/ttyACM0")
        self.declare_parameter("baudrate", 115200)
        self.declare_parameter("max_speed", 1000)
        self.declare_parameter("max_linear_vel", 1.5)    # m/s mapped to max_speed
        self.declare_parameter("max_angular_vel", 2.0)   # rad/s
        self.declare_parameter("invert_left", False)
        self.declare_parameter("invert_right", False)

        self.port = self.get_parameter("port").value
        self.baudrate = self.get_parameter("baudrate").value
        self.max_speed = int(self.get_parameter("max_speed").value)
        self.max_linear_vel = float(self.get_parameter("max_linear_vel").value)
        self.max_angular_vel = float(self.get_parameter("max_angular_vel").value)
        self.invert_left = bool(self.get_parameter("invert_left").value)
        self.invert_right = bool(self.get_parameter("invert_right").value)

        # Open serial connection
        self.serial = None
        try:
            self.serial = serial.Serial(self.port, baudrate=self.baudrate, timeout=1)
            self.get_logger().info(
                f"Connected to STM32 on '{self.port}' at {self.baudrate} baud (max_speed={self.max_speed})"
            )
        except serial.SerialException as exc:
            self.get_logger().error(f"Failed to open serial port '{self.port}': {exc}")
            self.get_logger().warn(
                "Verify STM32 connection, permissions (sudo usermod -a -G dialout $USER), "
                "or pass port parameter: --ros-args -p port:=/dev/ttyUSB0"
            )

        self.subscriber = self.create_subscription(
            Twist,
            topic="cmd_vel",
            callback=self.cmd_vel_callback,
            qos_profile=10,
        )

    def cmd_vel_callback(self, msg: Twist):
        if self.serial is None or not self.serial.is_open:
            return

        linear = msg.linear.x
        angular = msg.angular.z

        # Differential drive normalized mixing
        # linear fraction (-1.0 to 1.0) and angular fraction (-1.0 to 1.0)
        lin_frac = linear / self.max_linear_vel if self.max_linear_vel > 0 else 0.0
        ang_frac = angular / self.max_angular_vel if self.max_angular_vel > 0 else 0.0

        # w_l = lin - ang, w_r = lin + ang
        raw_left = (lin_frac - ang_frac) * self.max_speed
        raw_right = (lin_frac + ang_frac) * self.max_speed

        # Safety clamp to [-max_speed, max_speed]
        speed_left = int(max(-self.max_speed, min(self.max_speed, raw_left)))
        speed_right = int(max(-self.max_speed, min(self.max_speed, raw_right)))

        if self.invert_left:
            speed_left = -speed_left
        if self.invert_right:
            speed_right = -speed_right

        # Transmit: speed1 (left), speed2 (right)
        command = f"{speed_left},{speed_right}\n"
        try:
            self.serial.write(command.encode("utf-8"))
            self.get_logger().debug(f"Sent: {speed_left},{speed_right}")
        except serial.SerialException as exc:
            self.get_logger().error(f"Serial write failed: {exc}")

    def destroy_node(self):
        if self.serial and self.serial.is_open:
            try:
                self.serial.write(b"0,0\n")
                self.serial.close()
                self.get_logger().info("Sent emergency stop (0,0) and closed serial port.")
            except Exception:
                pass
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    interface = MotorInterface()
    try:
        rclpy.spin(interface)
    except KeyboardInterrupt:
        pass
    finally:
        interface.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

