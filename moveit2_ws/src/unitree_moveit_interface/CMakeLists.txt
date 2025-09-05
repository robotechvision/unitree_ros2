cmake_minimum_required(VERSION 3.5)
project(unitree_movegroup_interface)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(graph_msgs REQUIRED)
find_package(moveit_visual_tools REQUIRED)

add_executable(move_group_interface_tutorial
    src/move_group_interface_tutorial.cpp
)

ament_target_dependencies(move_group_interface_tutorial
    rclcpp
    moveit_ros_planning_interface
    geometry_msgs
    std_msgs
    tf2_ros
    graph_msgs
    moveit_visual_tools
)

install(TARGETS move_group_interface_tutorial
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
