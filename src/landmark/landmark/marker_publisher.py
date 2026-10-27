import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
import yaml
import os

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

LANDMARK_FILE = os.path.expanduser(
    "~/IRC26/src/landmark/config/landmarks.yaml"
)

# ------------------------------------------------------------------
# Marker Publisher Node
# ------------------------------------------------------------------

class MarkerPublisher(Node):

    def __init__(self):
        super().__init__('marker_publisher')

        self.publisher = self.create_publisher(
            Marker,
            '/landmark_markers',
            10
        )

        # Publish markers periodically so RViz can reconnect anytime
        self.timer = self.create_timer(1.0, self.publish_markers)

        self.get_logger().info("Marker Publisher started")

    # --------------------------------------------------------------

    def publish_markers(self):
        if not os.path.exists(LANDMARK_FILE):
            return

        with open(LANDMARK_FILE, 'r') as f:
            data = yaml.safe_load(f) or {}

        landmarks = data.get('landmarks', [])
        if not landmarks:
            return

        now = self.get_clock().now().to_msg()

        for lm in landmarks:
            marker = Marker()

            marker.header.frame_id = "map"
            marker.header.stamp = now

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

            # Color from YAML
            r, g, b = lm['color']
            marker.color.r = float(r)
            marker.color.g = float(g)
            marker.color.b = float(b)
            marker.color.a = 1.0

            self.publisher.publish(marker)

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    rclpy.init()
    node = MarkerPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
