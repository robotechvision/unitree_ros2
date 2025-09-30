#!/usr/bin/bash

RUST_LOG=info ros2 run zenoh_bridge_dds zenoh_bridge_dds -d $1 -a "\
^/rt/lowstate$|\
^/rt/lowcmd$|\
^/rt/tf$|\
^/rt/tf_static$|\
^/rt/camera/d485/color/image_raw/compressed$|\
^/rt/camera/d485/depth/color/points$|\
^/rt/object_detection_viz/compressed$|\
^/rt/objects3d$|\
^/rt/livox/lidar$|\
^$"
