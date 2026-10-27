import rclpy
from rclpy.node import Node
import serial

from arm_ctrl_msgs.msg import Arm


class ArmInterface(Node):
	def __init__(self):
		super().__init__("arm_interface")
		self.serial = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=1)
		self.subscriber = self.create_subscription(
			Arm,
			topic="arm_cmd",
			callback=self.arm_cmd_callback,
			qos_profile=10,
		)

	def arm_cmd_callback(self, msg: Arm):
		servo1_len = len(msg.servo1_angle)
		servo2_len = len(msg.servo2_angle)

		servo1_data = ",".join(f"{v:.3f}" for v in msg.servo1_angle)
		servo2_data = ",".join(f"{v:.3f}" for v in msg.servo2_angle)

		data = (
			f"{int(msg.base)},"
			f"{int(msg.link1)},{int(msg.link2)},{int(msg.link3)},"
			f"{int(msg.servo1_dir)},{int(msg.servo2_dir)},"
			f"{servo1_len},{servo1_data},"
			f"{servo2_len},{servo2_data},"
			f"{int(msg.tool)}\n"
		)

		self.get_logger().info(
			"Arm cmd -> base=%s link1=%s link2=%s link3=%s servo1_dir=%s servo2_dir=%s "
			"servo1_angle=%s servo2_angle=%s tool=%s",
			msg.base,
			msg.link1,
			msg.link2,
			msg.link3,
			msg.servo1_dir,
			msg.servo2_dir,
			list(msg.servo1_angle),
			list(msg.servo2_angle),
			msg.tool,
		)

		self.serial.write(data.encode())


def main(args=None):
	rclpy.init(args=args)
	interface = ArmInterface()
	rclpy.spin(interface)
	interface.destroy_node()
	rclpy.shutdown()


if __name__ == "__main__":
	main()