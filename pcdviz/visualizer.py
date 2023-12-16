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

import datetime
import logging
import time

import open3d as o3d
from open3d.visualization import gui, rendering

from pcdviz.io.image import save_gif

KEY_A = 65
KEY_N = 78
KEY_LEFT_ARROW = 75
KEY_RIGHT_ARROW = 77
KEY_UP_ARROW = 72
KEY_DOWN_ARROW = 80


class Visualizer:

    SOLID_NAME = "Solid Color"
    LABELS_NAME = "Label Colormap"

    def __init__(self):
        self._init_vis()
        self.save_gif = False

    def _init_vis(self):
        self._vis = o3d.visualization.VisualizerWithKeyCallback()
        self._vis.create_window()
        # options
        self._vis.get_render_option().line_width = 1
        self._vis.get_render_option().point_size = 1
        # self._vis.get_render_option().show_coordinate_frame = True

        # callback
        self._vis.register_key_callback(KEY_A, self._key_capture_callback)
        self._vis.register_key_callback(KEY_N, self._key_next_callback)

    def _init_data(self, dataset):
        self._dataset = dataset
        self._items = self._dataset.items()

    def __exit__(self):
        self._vis.destroy_window()

    def _key_capture_callback(self, vis):
        vis.capture_screen_image("{}.png".format(datetime.datetime.now()))

    def _key_next_callback(self, vis):
        image_datas = []
        geometries = next(self._items, None)
        if geometries:
            vis.clear_geometries()
            vis.add_geometry(geometries['pointcloud'])
            for bbox in geometries['bboxes']:
                vis.add_geometry(bbox)
            if self.save_gif:
                image_data = vis.capture_screen_float_buffer()
                image_datas.append(image_data)
                save_gif(image_datas, "test.gif")

    def visualize_dataset(self, dataset):
        """Display the dataset

        Args:
            dataset (_type_): _description_
        """
        self._init_data(dataset)
        # first frame, next will display by callback(_key_next_callback)
        geometries = next(self._items, None)
        if geometries:
            self._vis.add_geometry(geometries['pointcloud'])
            for bbox in geometries['bboxes']:
                self._vis.add_geometry(bbox)
        self._vis.run()

    def visualize(self, data=[]):
        """Display a frame of point cloud or image, along with predicted and true values

        Args:
            data (_type_): A frame of PCD or image
            predict (_type_, optional): _description_. Defaults to None.
            ground_truth (_type_, optional): _description_. Defaults to None.
        """
        if data is None:
            logging.error("Data not exist!")
            return

        data = data if isinstance(data, list) else [data]
        for d in data:
            self._vis.add_geometry(d)
        self._vis.run()

    def play_dataset(self, dataset):
        self._init_data(dataset)
        self._vis.register_animation_callback(self._key_next_callback)
        self._vis.run()

    def _init_user_interface(self, title, width, height):
        self.window = gui.Application.instance.create_window(
            title, width, height)
        # self.window.set_on_layout(self._on_layout)

        em = self.window.theme.font_size

        self._3d = gui.SceneWidget()
        self._3d.enable_scene_caching(True)
        self._3d.scene = rendering.Open3DScene(self.window.renderer)
        self.window.add_child(self._3d)

    def setup_camera(self):
        """Set view perspective
        """
        bounds = self._3d.scene.bounding_box
        center = bounds.get_center()
        self._3d.setup_camera(60, bounds, center)
        self._3d.look_at(center, center - [0, 0, 100], [0, -1, 0])
