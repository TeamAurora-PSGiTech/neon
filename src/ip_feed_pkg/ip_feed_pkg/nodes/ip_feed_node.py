#!/usr/bin/env python3

import time
import math
import os
from datetime import datetime

import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix


class GPSOverlayNode(Node):
    def __init__(self):
        super().__init__('gps_overlay_node')

        self.declare_parameter('video_source', '0')

        self.declare_parameter('gps_topic', 'gps')

        self.video_source = self.get_parameter('video_source').value
        self.gps_topic = self.get_parameter('gps_topic').value

        self.lat = float('nan')
        self.lon = float('nan')
        self.alt = float('nan')
        self.has_fix = False

        self.create_subscription(
            NavSatFix,
            self.gps_topic,
            self.gps_callback,
            10
        )

        # ---------------- VIDEO ----------------
        self.cap = self.open_video(self.video_source)

        os.makedirs('screenshots', exist_ok=True)
        self.get_logger().info("Press 'c' to capture | 'q' to quit")

    # ------------------------------------------------

    def gps_callback(self, msg: NavSatFix):
        if msg.status.status < 0:
            return

        self.lat = msg.latitude
        self.lon = msg.longitude
        self.alt = msg.altitude
        self.has_fix = not math.isnan(self.lat) and not math.isnan(self.lon)

    # ------------------------------------------------

    def open_video(self, source):
        try:
            src = int(source)
        except ValueError:
            src = source

        cap = cv2.VideoCapture(src)
        if not cap.isOpened():
            cap = cv2.VideoCapture(src, cv2.CAP_FFMPEG)

        if not cap.isOpened():
            self.get_logger().error(f"Failed to open video source: {source}")
            raise RuntimeError("Video open failed")

        return cap

    # ------------------------------------------------

    def overlay_text(self, image, text, org, scale=0.7, thickness=2, pad=6):
        font = cv2.FONT_HERSHEY_SIMPLEX

        (w, h), _ = cv2.getTextSize(text, font, scale, thickness)
        x, y = org

        cv2.rectangle(
            image,
            (x - pad, y - h - pad),
            (x + w + pad, y + pad // 2),
            (0, 0, 0),
            cv2.FILLED
        )

        cv2.putText(
            image,
            text,
            org,
            font,
            scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA
        )

    # ------------------------------------------------

    def run(self):
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0)

            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            if self.has_fix:
                gps_text = f"Lat: {self.lat:.6f}  Lon: {self.lon:.6f}  Alt: {self.alt:.1f} m"
            else:
                gps_text = "No GPS fix"

            self.overlay_text(frame, gps_text, (10, 30), scale=1.0, thickness=2, pad=8)

            ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
            self.overlay_text(frame, ts, (10, 60))

            cv2.imshow("Video with GPS", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

            if key == ord('c'):
                self.capture(frame)

        self.cleanup()

    # ------------------------------------------------

    def capture(self, frame):
        stamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

        if self.has_fix:
            name = f"screenshots/screenshot_{stamp}_lat{self.lat:.6f}_lon{self.lon:.6f}.jpg"
        else:
            name = f"screenshots/screenshot_{stamp}_nofix.jpg"

        cv2.imwrite(name, frame)
        self.get_logger().info(f"Saved {name}")

    # ------------------------------------------------

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()


# ==================================================

def main():
    rclpy.init()
    node = GPSOverlayNode()

    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
