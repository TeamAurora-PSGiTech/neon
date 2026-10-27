import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image, NavSatFix
from cv_bridge import CvBridge

import cv2
import numpy as np
import json
from datetime import datetime
import math


class PanoramaNode(Node):
    def __init__(self):
        super().__init__('panorama_node')

        self.bridge = CvBridge()
        self.current_frame = None
        self.panorama_frames = []
        self.single_count = 0

        # GPS storage
        self.gps_fix = None
        self.gps_received = False
        self.gps_accuracy = None  # meters

        # RGB subscription
        self.create_subscription(
            Image,
            '/camera/camera/color/image_raw',
            self.image_cb,
            10
        )

        # GPS subscription
        self.create_subscription(
            NavSatFix,
            '/fix',
            self.gps_cb,
            10
        )

        self.get_logger().info("Panorama node started (RGB only)")

    # ---------------- CALLBACKS ----------------

    def image_cb(self, msg):
        self.current_frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        display = self.current_frame.copy()

        cv2.putText(
            display,
            "a: single | s: pano frame | q: stitch & exit",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.imshow("Panorama Capture", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('a'):
            self.save_single()
        elif key == ord('s'):
            self.capture_panorama_frame()
        elif key == ord('q'):
            self.finish()

    def gps_cb(self, msg):
        if msg.status.status < 0:
            return

        self.gps_fix = msg
        self.gps_received = True

        if msg.position_covariance_type != NavSatFix.COVARIANCE_TYPE_UNKNOWN:
            cov = msg.position_covariance
            self.gps_accuracy = math.sqrt(cov[0] + cov[4])
        else:
            self.gps_accuracy = None

    # ---------------- SINGLE IMAGE ----------------

    def save_single(self):
        if self.current_frame is None:
            return

        self.single_count += 1
        img_name = f"single_image_{self.single_count}.jpg"
        meta_name = f"single_image_{self.single_count}.json"

        cv2.imwrite(img_name, self.current_frame)

        metadata = {
            "type": "single_image",
            "image": img_name,
            "timestamp": datetime.now().isoformat()
        }

        with open(meta_name, "w") as f:
            json.dump(metadata, f, indent=4)

    # ---------------- PANORAMA ----------------

    def capture_panorama_frame(self):
        if self.current_frame is None:
            return

        self.panorama_frames.append(self.current_frame.copy())

    def draw_gps_on_image(self, image):
        # ✅ DO NOTHING if GPS is not fixed
        if not self.gps_received:
            return

        h, w = image.shape[:2]

        lat = self.gps_fix.latitude
        lon = self.gps_fix.longitude
        alt = self.gps_fix.altitude

        text = f"Lat: {lat:.6f}  Lon: {lon:.6f}  Alt: {alt:.2f} m"

        # Background strip
        cv2.rectangle(image, (0, h - 40), (w, h), (0, 0, 0), -1)

        # Text
        cv2.putText(
            image,
            text,
            (10, h - 12),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

    def finish(self):
        cv2.destroyAllWindows()

        if len(self.panorama_frames) < 2:
            return

        stitcher = cv2.Stitcher_create(cv2.Stitcher_PANORAMA)
        status, pano = stitcher.stitch(self.panorama_frames)

        if status != cv2.Stitcher_OK:
            return

        # Draw GPS ONLY if fixed
        self.draw_gps_on_image(pano)

        cv2.imwrite("panorama.jpg", pano)

        metadata = {
            "type": "panorama",
            "image": "panorama.jpg",
            "frames_used": len(self.panorama_frames),
            "gps": {
                "latitude": self.gps_fix.latitude if self.gps_received else None,
                "longitude": self.gps_fix.longitude if self.gps_received else None,
                "altitude": self.gps_fix.altitude if self.gps_received else None,
                "accuracy_m": self.gps_accuracy,
                "cardinal_direction": ""
            },
            "timestamp": datetime.now().isoformat()
        }

        with open("panorama.json", "w") as f:
            json.dump(metadata, f, indent=4)

        self.destroy_node()
        rclpy.shutdown()


def main():
    rclpy.init()
    node = PanoramaNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

