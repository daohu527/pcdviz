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
from pcdviz.util import euler_to_rotation_matrix, to_euler


class Nuscenes(BaseDataset):
    def __init__(self, dataset_path, **kwargs):
        self.name = "nuScenes"
        self.dataset_path = dataset_path
        self.version = 'v1.0-mini'
        self.table_names = ['attribute', 'calibrated_sensor', 'category',
                            'instance', 'log', 'map', 'sample_annotation',
                            'sample_data', 'sample', 'scene', 'sensor',
                            'visibility']
        # schema -> {table_name: {}}
        self.schema_dict = dict()
        # sample_data -> {sample_token: [sample_data]}
        self.sample_data_dict = defaultdict(list)
        # sample_annotation -> {sample_token: [sample_annotation]}
        self.sample_annotation_dict = defaultdict(list)
        self._load_data()

    def __getitem__(self):
        pass

    def __len__(self):
        pass

    @property
    def scene(self):
        return self.schema_dict['scene']

    @property
    def sample(self):
        return self.schema_dict['sample']

    @property
    def sample_data(self):
        return self.schema_dict['sample_data']

    @property
    def sample_annotation(self):
        return self.schema_dict['sample_annotation']

    @property
    def calibrated_sensor(self):
        return self.schema_dict['calibrated_sensor']

    @property
    def sensor(self):
        return self.schema_dict['sensor']

    def _load_data(self):
        # Init schema_dict
        for table_name in self.table_names:
            file_path = os.path.join(
                self.dataset_path, self.version, "{}.json".format(table_name))
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.schema_dict[table_name] = {d['token']: d for d in data}
        # Init sample_data_dict
        for token, sample_data in self.sample_data.items():
            sample_token = sample_data['sample_token']
            self.sample_data_dict[sample_token].append(sample_data)
        # Init sample_annotation_dict
        for token, sample_annotation in self.sample_annotation.items():
            sample_token = sample_annotation['sample_token']
            self.sample_annotation_dict[sample_token].append(sample_annotation)

    def _get_samples(self):
        for token, scene in self.scene.items():
            sample_token = scene['first_sample_token']
            while sample_token:
                sample = self.sample[sample_token]
                sample_token = sample['next']
                yield sample

    def items(self):
        for sample in self._get_samples():
            sample_token = sample['token']
            for sample_data in self.sample_data_dict[sample_token]:
                if sample_data['is_key_frame']:
                    file_path = os.path.join(
                        self.dataset_path, sample_data['filename'])
                    calibrated_sensor_token = sample_data['calibrated_sensor_token']
                    sensor_token = self.calibrated_sensor[calibrated_sensor_token]['sensor_token']
                    sensor = self.sensor[sensor_token]
                    if sensor['modality'] == 'lidar':
                        pointcloud = Nuscenes.create_pointcloud(file_path)
            bboxes = []
            for sample_annotation in self.sample_annotation_dict[sample_token]:
                bbox = Nuscenes.create_oriented_bounding_box(sample_annotation)
                # bboxes.append(bbox)
            yield {"pointcloud": pointcloud,
                   "bboxes": bboxes}

    @staticmethod
    def create_pointcloud(pcd_file):
        points = Nuscenes.read_pcd(pcd_file)
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points[:, :3])
        return pcd

    @staticmethod
    def create_oriented_bounding_box(sample_annotation):
        translation = sample_annotation['translation']
        size = sample_annotation['size']
        w, x, y, z = sample_annotation['rotation']
        roll, pitch, yaw = to_euler(w, x, y, z)
        rotation_mat = euler_to_rotation_matrix(roll, pitch, yaw)
        bbox = o3d.geometry.OrientedBoundingBox(
            translation, rotation_mat, size)
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
