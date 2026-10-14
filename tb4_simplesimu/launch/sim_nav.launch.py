import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_tb4_sim = get_package_share_directory('turtlebot4_ignition_bringup')
    
    default_map_path = os.path.expanduser('~/tb4_simplesimu/maps/map.yaml')

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=default_map_path,
        description='Full path to map file'
    )

    tb4_sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_tb4_sim, 'launch', 'turtlebot4_ignition.launch.py')
        ),
        launch_arguments={
            'slam': 'false',
            'nav2': 'true',
            'rviz': 'true',
            'world': 'maze',
            'map': LaunchConfiguration('map')
        }.items()
    )

    return LaunchDescription([
        map_arg,
        tb4_sim_launch
    ])
