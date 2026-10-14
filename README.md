```markdown
# Bài thực hành 04 – TurtleBot 4 Simulation (SLAM Toolbox & Nav2)

Dự án mô phỏng robot **TurtleBot 4** trong môi trường **Gazebo (Ignition Fortress)** sử dụng **ROS 2 Humble**. Dự án bao gồm quy trình khép kín: Tự động xây dựng bản đồ 2D (SLAM Toolbox), làm sạch bản đồ, định vị vị trí robot (AMCL) và điều hướng tự động bằng Nav2 trên bản đồ đã lưu.

##  1. Cấu trúc Repository

```text
tb4_simplesimu/
├── launch/
│   ├── sim.launch.py            # TurtleBot 4 trong Gazebo
│   ├── mapping.launch.py        # SLAM Toolbox + RViz2
│   ├── localization.launch.py   # Nạp map + AMCL + RViz2
│   ├── navigation.launch.py     # Nav2 Autonomous Navigation
│   ├── sim_slam.launch.py       # Tích hợp Gazebo + SLAM Toolbox + RViz2
│   ├── sim_nav.launch.py        # Tích hợp Gazebo + AMCL + Nav2 + RViz2
│   ├── drive_mapping.launch.py  # Gazebo + SLAM + RViz2 + Bảng điều khiển Tkinter
│   └── auto_mapping.launch.py   # Gazebo + SLAM + RViz2 + Node tự khám phá
├── scripts/
│   ├── auto_mapper.py           # Node Python tự động lái xe né vật cản & lưu map
│   ├── control_panel.py         # Bảng điều khiển thanh trượt (Tkinter) & nút lưu map
│   ├── auto_explore.py          # Node tự khám phá theo biên (Frontier Exploration)
│   ├── wall_follow.py           # Thuật toán bám tường từ dữ liệu LiDAR
│   ├── check_topics.sh          # Script kiểm tra dữ liệu topic (/scan, /odom, /cmd_vel)
│   ├── save_map.sh              # Script lưu bản đồ tự động
│   └── lighten_sensors.sh       # Giảm tải tần số cảm biến (tối ưu CPU/GPU)
├── maps/                        # Chứa map.yaml + map.pgm (gốc) và map_clean.* (đã xử lý)
├── tools/
│   └── clean_map.py             # Script làm sạch thân đồ nội thất trong file map.pgm
├── CMakeLists.txt               # Cấu hình biên dịch CMake
└── package.xml                  # Định nghĩa dependencies của package ROS 2

```

---

##  2. Cài đặt & Tối ưu Hệ thống

### Bước 2.1: Cài đặt các gói phụ thuộc (Dependencies)

```bash
sudo apt update
sudo apt install -y \
  python3-tk \
  ros-humble-turtlebot4-simulator \
  ros-humble-turtlebot4-desktop \
  ros-humble-turtlebot4-navigation \
  ros-humble-slam-toolbox \
  ros-humble-nav2-bringup \
  ros-humble-nav2-map-server \
  ros-humble-teleop-twist-keyboard

```

### Bước 2.2: Tạo Workspace và Biên dịch Package

```bash
# Tạo workspace và liên kết package
mkdir -p ~/colcon_ws/src
ln -s ~/tb4_simplesimu ~/colcon_ws/src/tb4_simplesimu

# Biên dịch workspace
cd ~/colcon_ws
colcon build --symlink-install
source install/setup.bash

# Tự động source workspace cho mỗi terminal mới
echo "source ~/colcon_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc

```

### Bước 2.3: Tối ưu đồ họa phần mềm (Nó giúp tránh đơ Gazebo / RViz2 trên card Intel/NVIDIA)

```bash
echo "export LIBGL_ALWAYS_SOFTWARE=1" >> ~/.bashrc
echo "export MESA_LOADER_DRIVER_NAME=llvmpipe" >> ~/.bashrc
source ~/.bashrc

```

---

## 3. Phần 1 & 2: Khởi chạy Mô phỏng & Tạo bản đồ (SLAM)

### Cách 1: Tự động chạy quét & Tự động lưu bản đồ (1 lệnh duy nhất)

```bash
# Terminal 1: Chạy mô phỏng SLAM
ros2 launch tb4_simplesimu sim_slam.launch.py world:=maze

# Terminal 2: Kích hoạt node tự khám phá né vật cản & tự lưu map sau 60s
ros2 run tb4_simplesimu auto_mapper.py

```

> **Kết quả**: Sau 60 giây, robot tự dừng và xuất 2 file `map.yaml` và `map.pgm` vào thư mục `~/tb4_simplesimu/maps/`.

---

### Cách 2: Lái robot bằng Bảng điều khiển GUI (Tkinter Control Panel)

```bash
ros2 launch tb4_simplesimu drive_mapping.launch.py world:=maze

```

* Sử dụng giao diện thanh trượt để tiến/lùi và xoay hướng.
* Nhấn nút **LƯU BẢN ĐỒ NGAY** trên giao diện để tự động ghi file ra thư mục `maps/`.

---

### Cách 3: Điều khiển bằng Bàn phím (Teleop) & Lưu thủ công

```bash
# Chạy teleop (đã bổ sung repeat_rate:=20.0 để đè timeout an toàn)
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/diffdrive_controller/cmd_vel_unstamped -p repeat_rate:=20.0

# Lưu bản đồ thủ công:
cd ~/tb4_simplesimu/maps
ros2 run nav2_map_server map_saver_cli -f map

```

---

### Cách 4: Làm sạch bản đồ (Tùy chọn)

Nếu muốn điền đầy các khoảng trống nội thất bên trong bản đồ:

```bash
python3 ~/tb4_simplesimu/tools/clean_map.py

```

---

##  4. Phần 3 & 4: Định vị (Localization - AMCL) & Điều hướng (Nav2)

Sau khi lưu map ở Phần 2, biên dịch lại workspace để nhận file map mới:

```bash
cd ~/colcon_ws && colcon build --packages-select tb4_simplesimu && source install/setup.bash

```

### Bước 4.1: Khởi chạy chế độ Navigation

```bash
ros2 launch tb4_simplesimu sim_nav.launch.py world:=maze map:=/home/huy/tb4_simplesimu/maps/map.yaml

```

### Bước 4.2: Định vị Robot (AMCL Localization)

1. Trên giao diện **RViz2**, bấm vào công cụ **`2D Pose Estimate`** trên thanh menu phía trên.
2. Nhấp chuột và kéo hướng tại vị trí của robot tương ứng với vị trí thực trong Gazebo.
3. Quan sát vệt tia LiDAR màu đỏ khớp hoàn toàn với đường viền tường màu đen trên bản đồ tĩnh.

### Bước 4.3: Tự động điều hướng đến điểm đích (Nav2 Goal)

1. Chọn công cụ **`Nav2 Goal`** trên RViz2.
2. Nhấp và kéo hướng chỉ định vị trí đích cần đến trong khoảng trống bản đồ.
3. Robot sẽ tự lập kế hoạch né vật cản và di chuyển chính xác đến điểm chỉ định.

---

## 5. Bảng xử lý sự cố (Troubleshooting)

| Sự cố | Nguyên nhân | Cách khắc phục |
| --- | --- | --- |
| **Xe di chuyển 0.5s rồi tự dừng** | Create 3 trigger safety motion timeout | Thêm tham số `-p repeat_rate:=20.0` khi chạy `teleop_twist_keyboard`. |
| **`Global Status: Error` / Map không hiện** | File `map.yaml` dùng đường dẫn tương đối | Mở `map.yaml` và chỉnh đường dẫn tuyệt đối: `image: /home/huy/tb4_simplesimu/maps/map.pgm`. |
| **RViz2 báo `Navigation: unknown**` | Nav2 Lifecycle chưa được kích hoạt | Mở terminal chạy: `ros2 run nav2_util lifecycle_bringup map_server`. |
| **Gazebo giật lag / Real Time Factor thấp** | LiDAR/Camera tốn quá nhiều tài nguyên CPU | Chạy script giảm tải cảm biến: `./scripts/lighten_sensors.sh`. |
| **Trùng tiến trình cũ bị treo** | Tiến trình ROS 2/Gazebo chạy ngầm | Chạy lệnh dọn dẹp: `pkill -9 -f rviz2; pkill -9 -f ignition`. |

```

```
