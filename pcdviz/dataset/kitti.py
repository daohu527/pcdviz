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

import glob
import logging
import os
from pathlib import Path

import numpy as np
import open3d as o3d


class KITTI(BaseDataset):
    """
      Car = 1
      Van = 2
      Truck = 3
      Pedestrian = 4
      Person_sitting = 5
      Cyclist = 6
      Tram = 7
      Misc = 8
      DontCare = 9
    """

    def __init__(self, dataset_path, **kwargs):
        self.name = 'KITTI'
        self.dataset_path = dataset_path
        self.file_names = self.get_sorted_file_names()

        assert len(self.file_names) != 0, "File not found in {}".format(
            self.dataset_path)

    def get_sorted_file_names(self):
        velodyne_path = os.path.join(self.dataset_path, "velodyne/")
        file_names = []
        for velodyne_file in glob.glob("{}*.bin".format(velodyne_path)):
            file_name = Path(velodyne_file).stem
            file_names.append(file_name)
        file_names.sort()
        return file_names

    def __getitem__(self):
        pass

    def __len__(self):
        return len(self.file_names)

    def items(self):
        for file_name in self.file_names:
            # create PointCloud
            velodyne_file = os.path.join(
                self.dataset_path, "velodyne/{}.bin".format(file_name))
            pointcloud = self.create_pointcloud(velodyne_file)

            # create OrientedBoundingBox
            calib_file = velodyne_file.replace(
                'velodyne', 'calib').replace('.bin', '.txt')
            label_file = calib_file.replace('calib', 'label_2')
            bboxes = self.create_oriented_bounding_box(label_file, calib_file)

            yield {"pointcloud": pointcloud,
                   "bboxes": bboxes}

    @staticmethod
    def create_pointcloud(velodyne_file):
        points = KITTI.read_velodyne(velodyne_file)
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points[:, :3])
        return pcd

    @staticmethod
    def create_oriented_bounding_box(label_file, calib_file):
        # read calib
        calib = KITTI.read_calib(calib_file)

        # create OrientedBoundingBox
        objs = KITTI.read_label(label_file, calib)
        bboxes = []
        rotation = np.eye(3, dtype=np.float32)
        for obj in objs:
            if obj["type"] != "DontCare":
                bbox = o3d.geometry.OrientedBoundingBox(
                    obj["location"], rotation, obj["dimensions"])
                # todo(zero): add color
                # bbox.color
                bboxes.append(bbox)
        return bboxes

    @staticmethod
    def read_image(file_path):
        pass

    @staticmethod
    def read_velodyne(file_path):
        if not Path(file_path).exists():
            logging.error("File not exist! {}".format(file_path))
            return None
        return np.fromfile(file_path, dtype=np.float32).reshape(-1, 4)

    @staticmethod
    def read_label(file_path, calib):
        labels = np.loadtxt(file_path, delimiter=' ', dtype=str, ndmin=2)
        objs = []
        for label in labels:
            # KITTI image coordinates
            image_bbox = np.array(
                [label[4], label[5], label[6], label[7]], dtype=np.float32)
            # x,y,z in KITTI camera coordinates
            camera_center = np.array(
                [label[11], label[12], label[13], 1.0], dtype=np.float32)

            # KITTI order is (height, width, length)
            size = np.array([label[10], label[9], label[8]], dtype=np.float32)

            # KITTI camera to velodyne coordinates
            velo_to_cam = np.transpose(
                calib['rect_4x4'] @ calib['Tr_velo_to_cam'])
            points = camera_center @ np.linalg.inv(velo_to_cam)
            velodyne_center = [points[0], points[1], points[2] + (size[2] / 2)]

            objs.append({
                "type": label[0],
                "truncated": float(label[1]),
                "occluded": int(label[2]),
                "alpha": float(label[3]),
                "bbox": image_bbox,
                "dimensions": size,
                "location": velodyne_center,
                "rotation_y": float(label[14]),
                "score": None})
        return objs

    @staticmethod
    def _extend_matrix(mat):
        mat = np.concatenate(
            [mat, np.array([[0., 0., 1., 0.]], dtype=mat.dtype)], axis=0)
        return mat

    @staticmethod
    def read_calib(file_path):
        if not Path(file_path).exists():
            logging.error("File not exist! {}".format(file_path))
            return None

        with open(file_path, 'r') as f:
            lines = f.readlines()

        obj = lines[0].strip().split(' ')[1:]
        P0 = np.array(obj, dtype=np.float32).reshape(3, 4)

        obj = lines[1].strip().split(' ')[1:]
        P1 = np.array(obj, dtype=np.float32).reshape(3, 4)

        obj = lines[2].strip().split(' ')[1:]
        P2 = np.array(obj, dtype=np.float32).reshape(3, 4)

        obj = lines[3].strip().split(' ')[1:]
        P3 = np.array(obj, dtype=np.float32).reshape(3, 4)

        P0 = KITTI._extend_matrix(P0)
        P1 = KITTI._extend_matrix(P1)
        P2 = KITTI._extend_matrix(P2)
        P3 = KITTI._extend_matrix(P3)

        # R0_rect is 3x3
        obj = lines[4].strip().split(' ')[1:]
        rect_4x4 = np.eye(4, dtype=np.float32)
        rect_4x4[:3, :3] = np.array(obj, dtype=np.float32).reshape(3, 3)

        obj = lines[5].strip().split(' ')[1:]
        Tr_velo_to_cam = np.eye(4, dtype=np.float32)
        Tr_velo_to_cam[:3] = np.array(obj, dtype=np.float32).reshape(3, 4)

        obj = lines[6].strip().split(' ')[1:]
        Tr_imu_to_velo = np.eye(4, dtype=np.float32)
        Tr_imu_to_velo[:3] = np.array(obj, dtype=np.float32).reshape(3, 4)

        return {"P0": P0,
                "P1": P1,
                "P2": P2,
                "P3": P3,
                "rect_4x4": rect_4x4,
                "Tr_velo_to_cam": Tr_velo_to_cam,
                "Tr_imu_to_velo": Tr_imu_to_velo}
