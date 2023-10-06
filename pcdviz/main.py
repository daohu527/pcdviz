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
import logging
import site
from pathlib import Path


from pcdviz.config.config import Config
from pcdviz.dataset.custom_dataset import CustomDataset
from pcdviz.dataset.kitti import KITTI
from pcdviz.visualizer import Visualizer


def _get_file_type(file_path: str) -> str:
    return os.path.splitext(file_path)[1]


def display_pointcloud(file_path):
    if not Path(file_path).exists():
        logging.error("File not exist! {}".format(file_path))
        return None

    vis = Visualizer()
    file_type = _get_file_type(file_path)[1:]
    pointcloud = CustomDataset.create_pointcloud(file_path, file_type)
    vis.visualize(pointcloud)


def display_frame(config):
    vis = Visualizer()

    geometries = []
    for input in config.inputs:
        input_type = input.get("name")
        if input_type == "pointcloud":
            lidar_file = input.get("path")
            file_type = input.get("type")
            fields = input.get("fields")
            color = input.get("color")
            transform = input.get("transform")

            geometry = CustomDataset.create_pointcloud(
                lidar_file=lidar_file, file_type=file_type, fields=fields,
                color=color, transform=transform)
            geometries.append(geometry)
        elif input_type == "oriented_bounding_box":
            label_file = input.get("path")
            format = input.get("format")
            color = input.get("color")
            transform = input.get("transform")
            scale = input.get("scale")

            geometry = CustomDataset.create_oriented_bounding_box(
                label_file=label_file, format=format, color=color,
                transform=transform, scale=scale)
            geometries.extend(geometry)
        else:
            logging.error("Skip unknown input type! {}".format(input_type))
    vis.visualize(geometries)


def display_dataset(config):
    dataset_conf = config.dataset
    dataset_name = dataset_conf.get("name")
    dataset_path = dataset_conf.get("path")
    if dataset_name == "KITTI":
        dataset = KITTI(dataset_path)

    vis = Visualizer()
    vis.visualize_dataset(dataset)


def reset_working_dir():
    system_install_config = os.path.join(sys.prefix, 'pcdviz/')
    user_install_config = os.path.join(site.USER_BASE, 'pcdviz/')
    if Path(user_install_config).exists():
        os.chdir(user_install_config)
        print("Current working dir is: {}".format(user_install_config))
    elif Path(system_install_config).exists():
        os.chdir(system_install_config)
        print("Current working dir is: {}".format(system_install_config))
    else:
        logging.error("Can't find working dir!")


def main(args=sys.argv):
    parser = argparse.ArgumentParser(
        description="point cloud viz.", prog="main.py")

    parser.add_argument(
        "-p", "--pcd", action="store", type=str, required=False,
        help="")

    parser.add_argument(
        "-c", "--cfg", action="store", type=str, required=False,
        help="")

    parser.add_argument(
        "--example", action="store", type=bool, required=False,
        nargs='?', const=True, help="Example mode")

    args = parser.parse_args(args[1:])

    # When running the example, we need to switch the working directory
    if args.example:
        reset_working_dir()

    # 1. display pointcloud then return
    if args.pcd:
        display_pointcloud(args.pcd)
        return

    # 2. display pointcloud and labels
    config = Config(args.cfg)
    if config.dataset:
        display_dataset(config)
    elif config.inputs:
        display_frame(config)
