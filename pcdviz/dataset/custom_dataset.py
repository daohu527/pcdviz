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

from pcdviz.dataset.base_dataset import BaseDataset

import logging
from pathlib import Path

import numpy as np
import open3d as o3d

from pcdviz.util import COLOR_MAP


def _fill_color(pointcloud, color):
    color = COLOR_MAP.get(color)
    if color:
        pointcloud.paint_uniform_color(color)


class CustomDataset(BaseDataset):
    def __init__(self) -> None:
        pass

    @staticmethod
    def create_pointcloud(lidar_file, file_type, fields=None, color=None,
                          transform=None):
        if file_type == "bin":
            points = CustomDataset.read_lidar(lidar_file, fields)
            pointcloud = o3d.geometry.PointCloud()
            pointcloud.points = o3d.utility.Vector3dVector(points[:, :3])
        elif file_type == "pcd":
            pointcloud = o3d.io.read_point_cloud(lidar_file)
        else:
            pointcloud = o3d.geometry.PointCloud()

        _fill_color(pointcloud, color)
        return pointcloud

    @staticmethod
    def read_lidar(file_path, fields=None):
        if not Path(file_path).exists():
            logging.error("File not exist! {}".format(file_path))
            return None
        # Todo(zero): need complete fields
        dim = int(fields) if fields else 4
        return np.fromfile(file_path, dtype=np.float32).reshape(-1, dim)

    @staticmethod
    def create_oriented_bounding_box(label_file, format, color=None,
                                     transform=None, scale=None):
        objs = CustomDataset.read_label(label_file, format)

        color = COLOR_MAP.get(color)
        bboxes = []
        for obj in objs:
            bbox = o3d.geometry.OrientedBoundingBox(
                obj["center"], obj["R"], obj["extent"])

            if color:
                bbox.color = color
            bboxes.append(bbox)
        return bboxes

    @staticmethod
    def read_label(file_path, format):
        labels = np.loadtxt(file_path, delimiter=' ', dtype=str)
        objs = []
        for label in labels:
            # x, y, z
            center = np.array(
                [label[1], label[2], label[3]], dtype=np.float32)

            # R
            # R = np.array([label[4], label[5], label[6]], dtype=np.float32)
            R = np.eye(3, 3)

            # length, width, height
            size = np.array([label[7], label[8], label[9]], dtype=np.float32)

            objs.append({
                "type": label[0],
                "center": center,
                "R": R,
                "extent": size})
        return objs
