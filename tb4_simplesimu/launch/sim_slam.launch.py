import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_tb4_sim = get_package_share_directory('turtlebot4_ignition_bringup')
    
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='maze',
        description='Ignition Gazebo World'
    )

    tb4_sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_tb4_sim, 'launch', 'turtlebot4_ignition.launch.py')
        ),
        launch_arguments={
            'slam': 'true',
            'nav2': 'false',
            'rviz': 'true',
            'world': LaunchConfiguration('world'),
            'x': '0.0',
            'y': '0.0',
            'z': '0.1'
        }.items()
    )

    return LaunchDescription([
        world_arg,
        tb4_sim_launch
    ])
