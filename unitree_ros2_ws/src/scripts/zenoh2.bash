#!/usr/bin/bash

RUST_LOG=info ros2 run zenoh_bridge_dds zenoh_bridge_dds -d $1 -a ".*"
