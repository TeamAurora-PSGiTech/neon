import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist


class JoyTwist(Node):
    def __init__(self):
        super().__init__('joy_twist')

        self.sub = self.create_subscription(Joy, '/joy', self.joy_cb, 10)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Declare ROS parameters
        self.declare_parameter("enable_button", 0)       # Deadman switch button index
        self.declare_parameter("linear_axis", 1)         # Left stick vertical
        self.declare_parameter("angular_axis", 0)        # Left stick horizontal
        self.declare_parameter("linear_speed_axis", 7)   # D-pad UP/DOWN
        self.declare_parameter("angular_speed_axis", 6)  # D-pad RIGHT/LEFT
        self.declare_parameter("linear_scale", 1.0)
        self.declare_parameter("angular_scale", 1.5)

        self.enable_button = int(self.get_parameter("enable_button").value)
        self.linear_axis = int(self.get_parameter("linear_axis").value)
        self.angular_axis = int(self.get_parameter("angular_axis").value)
        self.linear_speed_axis = int(self.get_parameter("linear_speed_axis").value)
        self.angular_speed_axis = int(self.get_parameter("angular_speed_axis").value)
        self.linear_scale = float(self.get_parameter("linear_scale").value)
        self.angular_scale = float(self.get_parameter("angular_scale").value)

        # ---- LIMITS ----
        self.min_linear = 0.05
        self.max_linear = 2.5
        self.min_angular = 0.1
        self.max_angular = 3.0

        # ---- DEBOUNCE STATE ----
        self.last_linear_dpad = 0.0
        self.last_angular_dpad = 0.0

    def joy_cb(self, msg):
        twist = Twist()

        # Bounds check
        if len(msg.buttons) <= self.enable_button:
            return

        # ---- DEADMAN ----
        if msg.buttons[self.enable_button] == 0:
            self.pub.publish(twist)
            return

        # ---- LINEAR SPEED ADJUSTMENT (D-pad) ----
        if len(msg.axes) > self.linear_speed_axis:
            linear_dpad = msg.axes[self.linear_speed_axis]
            if linear_dpad != self.last_linear_dpad:
                if linear_dpad == 1.0:
                    self.linear_scale = min(self.max_linear, self.linear_scale * 1.1)
                elif linear_dpad == -1.0:
                    self.linear_scale = max(self.min_linear, self.linear_scale * 0.9)
            self.last_linear_dpad = linear_dpad

        # ---- ANGULAR SPEED (e / c) ----
        angular_dpad = msg.axes[self.angular_speed_axis]
        if angular_dpad != self.last_angular_dpad:
            if angular_dpad == 1.0:
                self.angular_scale *= 1.1
            elif angular_dpad == -1.0:
                self.angular_scale *= 0.9

        self.last_angular_dpad = angular_dpad

        # Clamp
        self.angular_scale = max(
            self.min_angular, min(self.angular_scale, self.max_angular))

        # ---- MOTION ----
        twist.linear.x = msg.axes[self.linear_axis] * self.linear_scale
        twist.angular.z = msg.axes[self.angular_axis] * self.angular_scale

        self.pub.publish(twist)


def main():
    rclpy.init()
    node = JoyTwist()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()

