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

import logging
import threading

import numpy as np
import open3d as o3d
from open3d.visualization import gui
from open3d.visualization import rendering

from pcdviz.dataset.kitti import KITTI

KEY_ENTER = 65

class Visualizer:

    SOLID_NAME = "Solid Color"
    LABELS_NAME = "Label Colormap"
    RAINBOW_NAME = "Colormap (Rainbow)"
    GREYSCALE_NAME = "Colormap (Greyscale)"
    COLOR_NAME = "RGB"

    def __init__(self, callback):
        self._gradient = rendering.Gradient()
        self._callback = callback

    def __exit__(self):
        pass

    def setup_camera(self):
        """Set view perspective
        """
        bounds = self._3d.scene.bounding_box
        center = bounds.get_center()
        self._3d.setup_camera(60, bounds, center)
        self._3d.look_at(center, center - [0, 0, 100], [0, -1, 0])

    def set_lut(self, attr_name, lut):
        self._attrname2lut[attr_name] = lut

    def visualize_dataset(self, dataset, indices):
        pass

    def visualize(self, data, prediction=[], ground_truth=[]):
        """Display a frame of point cloud or image, along with predicted and true values

        Args:
            data (_type_): A frame of PCD or image
            predict (_type_, optional): _description_. Defaults to None.
            ground_truth (_type_, optional): _description_. Defaults to None.
        """
        if data is None:
            logging.error("Data not exist!")
            return

        vis = o3d.visualization.VisualizerWithKeyCallback()
        vis.create_window()
        # options
        vis.get_render_option().line_width = 1
        vis.get_render_option().point_size = 1
        vis.get_render_option().show_coordinate_frame = True
        # callback
        vis.register_key_callback(KEY_ENTER, self._callback)

        # pcd
        vis.add_geometry(data)

        # label
        for bbox in prediction:
            vis.add_geometry(bbox)
        vis.run()

    def _init_data(self, data):
        pcd = o3d.io.read_point_cloud(data)
        material = self._get_material()
        self._3d.scene.add_geometry("pcd", pcd, material)

    def _load_geometries(self, names, ui_done_callback):
        def load_thread():
            gui.Application.instance.post_to_main_thread(
                self.window, ui_done_callback)
        threading.Thread(target=load_thread).start()

    def _update_gradient(self):
        self._gradient.points = [
            rendering.Gradient.Point(0.0, [1.0, 0.0, 1.0, 1.0])
        ]

    def _get_material(self):
        self._update_gradient()
        material = rendering.MaterialRecord()
        material.shader = "unlitGradient"
        material.gradient = self._gradient
        material.scalar_min = 0
        material.scalar_max = 100
        # material.base_color = [1.0, 0.0, 0.0, 0.0]
        return material

    def _update_bounding_boxes(self):
        pass

    def _update_geometry(self):
        self._3d.force_redraw()

    def _init_user_interface(self, title, width, height):
        self.window = gui.Application.instance.create_window(
            title, width, height)
        # self.window.set_on_layout(self._on_layout)

        em = self.window.theme.font_size

        self._3d = gui.SceneWidget()
        self._3d.enable_scene_caching(True)
        self._3d.scene = rendering.Open3DScene(self.window.renderer)
        self.window.add_child(self._3d)

    def _visualize(self, title, width, height):
        gui.Application.instance.initialize()
        self._init_user_interface(title, width, height)

        self._3d.scene.downsample_threshold = 400000

        def on_done_ui():
            self._update_bounding_boxes()
            # self._set_shader(self.SOLID_NAME, force_update=True)

            self._update_geometry()
            self.setup_camera()

        self._load_geometries([], on_done_ui)

        gui.Application.instance.run()


if __name__ == "__main__":
    vis = Visualizer()
    dataset = KITTI("../data/kitti/")
    for data in dataset.get_data():
        vis.visualize(data["pointcloud"], data["bboxes"])
