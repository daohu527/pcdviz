#!/usr/bin/env python

# Copyright 2023 daohu527 <daohu527@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import argparse
import sys
import datetime

import open3d as o3d

from pcdviz.visualizer import Visualizer
from pcdviz.dataset.kitti import KITTI

def _get_file_type(file_path : str) -> str:
  return os.path.splitext(file_path)[1]

def _key_callback(vis):
    vis.capture_screen_image("{}.png".format(datetime.datetime.now()))

def display_frame_with_calib(lidar_file, label_file, calib_file):
    vis = Visualizer(_key_callback)

    file_type = _get_file_type(lidar_file)
    if file_type == ".bin":
        pointcloud = KITTI.create_pointcloud(lidar_file)
    elif file_type == ".pcd":
        pointcloud = o3d.io.read_point_cloud(lidar_file)
    
    bboxes = KITTI.create_oriented_bounding_box(label_file, calib_file)
    vis.visualize(pointcloud, bboxes)


def main(args=sys.argv):
    parser = argparse.ArgumentParser(
        description="point cloud viz.", prog="main.py")

    parser.add_argument(
        "--lidar_file", action="store", type=str, required=False,
        help="")
    parser.add_argument(
        "--label_file", action="store", type=str, required=False,
        help="")
    parser.add_argument(
        "--calib_file", action="store", type=str, required=False,
        help="")

    args = parser.parse_args(args[1:])

    display_frame_with_calib(args.lidar_file, args.label_file, args.calib_file)
