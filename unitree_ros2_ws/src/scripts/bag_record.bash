#!/usr/bin/bash
ros2 bag record --include-hidden-topics `ros2 topic list --include-hidden-topics -v | grep -E "publishers?$" | grep -oE " /[a-zA-Z0-9/_-]*" | grep -o "[^ ]*" | grep -E "\
^/detected_image_objects$|\
^/camera/d435/color/image_raw/compressed$|\
^/camera/d435/color/camera_info$|\
^/camera/d435/depth/camera_info$|\
^/camera/d435/depth/image_rect_raw$|\
^/camera/d435/depth/color/points$|\
^/livox/lidar$|\
^/joint_states$|\
^/tf$|\
^/tf_static$|\ 
^/ekf_odom/odom$|\ 
^/unitree/odom$|\ 
^/imu/data$|\ 
^/site/odom$|\ 
^/site/odom_recovarianced$|\ 
^$"`
