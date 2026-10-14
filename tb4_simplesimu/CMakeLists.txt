cmake_minimum_required(VERSION 3.8)
project(tb4_simplesimu)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  launch
  maps
  config
  scripts
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/auto_mapper.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
