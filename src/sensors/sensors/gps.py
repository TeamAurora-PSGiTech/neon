import rclpy
from rclpy.node import Node
import serial
import pynmea2
from sensor_msgs.msg import NavSatFix

class GPSInterface(Node):
    def __init__(self):
        super().__init__("gps_interface")
        self.serial_port = "/dev/ttyACM0"
        try:
            self.serial = serial.Serial(self.serial_port, baudrate=115200, timeout=1)
        except serial.SerialException as exc:
            self.serial = None
            self.get_logger().error(f"Unable to open {self.serial_port}: {exc}")
        self.publisher = self.create_publisher(NavSatFix, 'gps', 10)
        self.coord = [float('nan'), float('nan'), 0.0]
        self.timer = self.create_timer(0.1, self.gps_callback)

    def gps_callback(self):
        if self.serial is None or not self.serial.is_open:
            self.get_logger().warn("Serial connection unavailable; skipping read.")
            return

        try:
            raw = self.serial.readline().decode(errors="ignore").strip()
        except serial.SerialException as exc:
            self.get_logger().warn(f"Serial read failed: {exc}")
            return

        if not raw.startswith("$GNRMC"):
            return

        try:
            nmea_msg = pynmea2.parse(raw)
        except pynmea2.ParseError:
            self.get_logger().debug("Failed to parse NMEA sentence.")
            return

        if getattr(nmea_msg, "status", "V") != "A":
            self.get_logger().info("No GPS fix yet.")
            return

        self.coord[0] = nmea_msg.latitude
        self.coord[1] = nmea_msg.longitude
        gps_msg = NavSatFix()
        gps_msg.header.stamp = self.get_clock().now().to_msg()
        gps_msg.header.frame_id = "gps"
        gps_msg.latitude = self.coord[0]
        gps_msg.longitude = self.coord[1]
        gps_msg.altitude = self.coord[2]
        self.publisher.publish(gps_msg)
        self.get_logger().info(f"Latitude: {self.coord[0]}, Longitude: {self.coord[1]}")

def main(args = None):
    rclpy.init(args=args)
    interface = GPSInterface()
    rclpy.spin(interface)
    interface.destroy_node()
    rclpy.shutdown()

if __name__=="__main__":
    main()
