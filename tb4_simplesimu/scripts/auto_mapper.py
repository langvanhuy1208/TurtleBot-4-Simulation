#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import random
import time
import os

class AutoMapper(Node):
    def __init__(self):
        super().__init__('auto_mapper')
        
        self.cmd_pub = self.create_publisher(Twist, '/diffdrive_controller/cmd_vel_unstamped', 10)
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        
        self.obstacle_ahead = False
        self.scan_received = False
        self.timer = self.create_timer(0.1, self.control_loop)
        
        self.start_time = time.time()
        self.explore_duration = 60  # Quét trong 60 giây
        self.map_saved = False

        self.get_logger().info('>>> AUTO MAPPER HOAT DONG - DANG TU DO DUONG... <<<')

    def scan_callback(self, msg):
        self.scan_received = True
        num_samples = len(msg.ranges)
        # Quét dải phía trước xe
        front_ranges = msg.ranges[:int(num_samples/8)] + msg.ranges[-int(num_samples/8):]
        valid_ranges = [r for r in front_ranges if r > 0.05 and not float('inf') == r and not float('nan') == r]
        
        # Nếu khoảng cách tới vật cản phía trước < 0.6m
        if valid_ranges and min(valid_ranges) < 0.6:
            self.obstacle_ahead = True
        else:
            self.obstacle_ahead = False

    def control_loop(self):
        if not self.scan_received or self.map_saved:
            return

        elapsed = time.time() - self.start_time
        if elapsed > self.explore_duration:
            self.stop_robot()
            self.save_map()
            self.map_saved = True
            return

        cmd = Twist()
        if self.obstacle_ahead:
            # Phát hiện kẹt/vật cản -> Lùi lại và xoay 90 độ
            cmd.linear.x = -0.15
            cmd.angular.z = 1.2
            self.get_logger().info('Gặp vật cản/Kẹt! Đang lùi và quay xe...', throttle_duration_sec=1.0)
        else:
            # Không có vật cản -> Tiến tới
            cmd.linear.x = 0.25
            cmd.angular.z = 0.0

        self.cmd_pub.publish(cmd)

    def stop_robot(self):
        cmd = Twist()
        self.cmd_pub.publish(cmd)

    def save_map(self):
        self.get_logger().info('>>> DANG LUU BAN DO... <<<')
        maps_dir = os.path.expanduser('~/tb4_simplesimu/maps')
        os.makedirs(maps_dir, exist_ok=True)
        map_path = os.path.join(maps_dir, 'map')

        os.system(f'ros2 run nav2_map_server map_saver_cli -f {map_path}')
        self.get_logger().info(f'>>> DA LUU MAP THANH CONG TAI: {map_path} <<<')

def main(args=None):
    rclpy.init(args=args)
    node = AutoMapper()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
