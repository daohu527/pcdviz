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

import json
import logging
import os
from collections import defaultdict
from pathlib import Path

import numpy as np
import open3d as o3d
from pcdviz.dataset.base_dataset import BaseDataset


class Nuscenes(BaseDataset):
    def __init__(self, dataset_path, **kwargs):
        self.name = "nuScenes"
        self.dataset_path = dataset_path
        self.version = 'v1.0-mini'

        self.category = self._load_table('category')
        self.attribute = self._load_table('attribute')
        self.visibility = self._load_table('visibility')
        self.instance = self._load_table('instance')
        self.sensor = self._load_table('sensor')
        self.calibrated_sensor = self._load_table('calibrated_sensor')
        self.ego_pose = self._load_table('ego_pose')
        self.log = self._load_table('log')
        self.scene = self._load_table('scene')
        self.sample = self._load_table('sample')
        self.sample_data = self._load_table('sample_data')
        self.sample_annotation = self._load_table('sample_annotation')
        self.map = self._load_table('map')

        # sample_data -> {sample_token: [sample_data]}
        self.sample_data_dict = defaultdict(list)
        # sample_annotation -> {sample_token: [sample_annotation]}
        self.sample_annotation_dict = defaultdict(list)
        self._load_data()

    def __getitem__(self):
        pass

    def __len__(self):
        pass

    def _load_table(self, table_name):
        file_path = os.path.join(
            self.dataset_path, self.version, "{}.json".format(table_name))
        with open(file_path, 'r') as f:
            data = json.load(f)
            return {d['token']: d for d in data}

    def _load_data(self):
        # Init sample_data_dict
        for token, sample_data in self.sample_data.items():
            sample_token = sample_data['sample_token']
            self.sample_data_dict[sample_token].append(sample_data)
        # Init sample_annotation_dict
        for token, sample_annotation in self.sample_annotation.items():
            sample_token = sample_annotation['sample_token']
            self.sample_annotation_dict[sample_token].append(sample_annotation)

    def _get_samples(self, scene_token):
        scene = self.scene[scene_token]
        sample_token = scene['first_sample_token']
        while sample_token:
            sample = self.sample[sample_token]
            sample_token = sample['next']
            yield sample

    def get_sample_data(self, sample_data_token):
        sample_data = self.sample_data[sample_data_token]
        if not sample_data['is_key_frame']:
            return None, None

        calibrated_sensor = self.calibrated_sensor.get(
            sample_data['calibrated_sensor_token'])
        sensor = self.sensor.get(calibrated_sensor['sensor_token'])
        ego_pose = self.ego_pose.get(sample_data['ego_pose_token'])
        file_path = os.path.join(self.dataset_path, sample_data['filename'])
        pointcloud = None
        if sensor['modality'] == 'lidar':
            pointcloud = Nuscenes.create_pointcloud(file_path)

        calib = {"ego_pose": ego_pose, "calibrated_sensor": calibrated_sensor}
        bboxes = []
        sample_annotations = self.sample_annotation_dict.get(
            sample_data['sample_token'])
        for sample_annotation in sample_annotations:
            bbox = Nuscenes.create_oriented_bounding_box(
                sample_annotation, calib)
            bboxes.append(bbox)
        return pointcloud, bboxes

    def items(self):
        for token, scene in self.scene.items():
            for sample in self._get_samples(scene['token']):
                sample_token = sample['token']
                for sample_data in self.sample_data_dict[sample_token]:
                    pointcloud, bboxes = self.get_sample_data(
                        sample_data['token'])
                    if pointcloud:
                        yield {"pointcloud": pointcloud, "bboxes": bboxes}

    @staticmethod
    def create_pointcloud(pcd_file):
        points = Nuscenes.read_pcd(pcd_file)
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points[:, :3])
        return pcd

    @staticmethod
    def create_oriented_bounding_box(sample_annotation, calib):
        translation = sample_annotation['translation']
        width, length, height = sample_annotation['size']
        rotation_mat = o3d.geometry.OrientedBoundingBox.get_rotation_matrix_from_quaternion(
            sample_annotation['rotation'])
        bbox = o3d.geometry.OrientedBoundingBox(
            translation, rotation_mat, [length, width, height])

        # world to vehicle coordinates
        rotation_mat = o3d.geometry.OrientedBoundingBox.get_rotation_matrix_from_quaternion(
            calib['ego_pose']['rotation'])
        bbox.translate(-np.array(calib['ego_pose']['translation']))
        bbox.rotate(np.linalg.inv(rotation_mat))
        # vehicle to sensor coordinates
        rotation_mat = o3d.geometry.OrientedBoundingBox.get_rotation_matrix_from_quaternion(
            calib['calibrated_sensor']['rotation'])
        bbox.translate(-np.array(calib['calibrated_sensor']['translation']))
        bbox.rotate(np.linalg.inv(rotation_mat))
        return bbox

    @staticmethod
    def read_image(file_path):
        pass

    @staticmethod
    def read_pcd(file_path):
        if not Path(file_path).exists():
            logging.error("File not exist! {}".format(file_path))
            return None
        return np.fromfile(file_path, dtype=np.float32).reshape((-1, 5))
