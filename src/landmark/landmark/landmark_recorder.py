import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
from tf2_ros import Buffer, TransformListener

import yaml
import os
import sys
import select
import termios
import tty

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

LANDMARK_FILE = os.path.expanduser(
    "~/IRC26/src/landmark/config/landmarks.yaml"
)

KEY_COLOR_MAP = {
    'l': ('red',        (1.0, 0.0, 0.0)),
    'a': ('light_blue', (0.4, 0.7, 1.0)),
    's': ('orange',     (1.0, 0.5, 0.0)),
    'd': ('brown',      (0.6, 0.3, 0.1)),
    'f': ('pink',       (1.0, 0.4, 0.7)),
    'g': ('yellow',     (1.0, 1.0, 0.0)),
    'h': ('purple',     (0.6, 0.2, 0.8)),
    'j': ('dark_blue',  (0.0, 0.0, 0.6)),
    'k': ('dark_green', (0.0, 0.5, 0.0)),
    ';': ('cyan',       (0.0, 1.0, 1.0)),
}

# ------------------------------------------------------------------
# Keyboard Handling (robust & non-blocking)
# ------------------------------------------------------------------

def get_key_non_blocking():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
        if rlist:
            return sys.stdin.read(1).lower()
        return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# ------------------------------------------------------------------
# Landmark Recorder Node
# ------------------------------------------------------------------

class LandmarkRecorder(Node):

    def __init__(self):
        super().__init__('landmark_recorder')

        # TF
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Marker publisher
        self.marker_pub = self.create_publisher(
            Marker, '/landmark_markers', 10
        )

        # Load existing landmarks
        self.marker_id = 0
        self.landmarks = self.load_landmarks()

        for lm in self.landmarks:
            self.publish_marker(lm)

        if self.landmarks:
            self.marker_id = max(lm['id'] for lm in self.landmarks) + 1

        # User info
        self.get_logger().info("Landmark Recorder Ready")
        self.get_logger().info("Press keys to record landmarks:")
        for k, v in KEY_COLOR_MAP.items():
            self.get_logger().info(f"  '{k}' → {v[0]}")

    # --------------------------------------------------------------

    def load_landmarks(self):
        if not os.path.exists(LANDMARK_FILE):
            return []

        with open(LANDMARK_FILE, 'r') as f:
            data = yaml.safe_load(f) or {}

        return data.get('landmarks', [])

    # --------------------------------------------------------------

    def save_landmarks(self):
        os.makedirs(os.path.dirname(LANDMARK_FILE), exist_ok=True)
        with open(LANDMARK_FILE, 'w') as f:
            yaml.safe_dump({'landmarks': self.landmarks}, f)

    # --------------------------------------------------------------

    def publish_marker(self, lm):
        marker = Marker()
        marker.header.frame_id = "map"
        marker.header.stamp = self.get_clock().now().to_msg()

        marker.ns = "landmarks"
        marker.id = lm['id']
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD

        marker.pose.position.x = lm['x']
        marker.pose.position.y = lm['y']
        marker.pose.position.z = 0.0
        marker.pose.orientation.w = 1.0

        marker.scale.x = 0.3
        marker.scale.y = 0.3
        marker.scale.z = 0.3

        r, g, b = lm['color']
        marker.color.r = r
        marker.color.g = g
        marker.color.b = b
        marker.color.a = 1.0

        self.marker_pub.publish(marker)

    # --------------------------------------------------------------

    def record_landmark(self, key):
        try:
            tf = self.tf_buffer.lookup_transform(
                'map',
                'base_link',
                rclpy.time.Time()
            )
        except Exception as e:
            self.get_logger().error(f"TF lookup failed: {e}")
            return

        color_name, color_rgb = KEY_COLOR_MAP[key]

        lm = {
            'id': self.marker_id,
            'x': tf.transform.translation.x,
            'y': tf.transform.translation.y,
            'color_name': color_name,
            'color': list(color_rgb),
        }

        self.landmarks.append(lm)
        self.save_landmarks()
        self.publish_marker(lm)

        self.get_logger().info(
            f"Saved {color_name} landmark {lm['id']} "
            f"at x={lm['x']:.2f}, y={lm['y']:.2f}"
        )

        self.marker_id += 1

    # --------------------------------------------------------------

    def check_keyboard(self):
        key = get_key_non_blocking()
        if key in KEY_COLOR_MAP:
            self.record_landmark(key)

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    rclpy.init()
    node = LandmarkRecorder()

    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
            node.check_keyboard()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
