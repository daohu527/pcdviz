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

import threading

import open3d as o3d
from open3d.visualization import gui
from open3d.visualization import rendering


class Visualizer:
  def __init__(self):
    pass

  def __exit__(self):
    pass
  
  def setup_camera(self):
    """Set view perspective
    """
    pass

  def visualize_dataset(self, dataset, indices):
    pass
  
  def visualize(self, data, prediction = None, ground_truth = None, width=1280, height=768):
    """Display a frame of point cloud or image, along with predicted and true values

    Args:
        data (_type_): A frame of PCD or image
        predict (_type_, optional): _description_. Defaults to None.
        ground_truth (_type_, optional): _description_. Defaults to None.
    """
    # todo(zero): load data
    self._visualize("Open3D", width, height)

  def _load_geometries(self, names, ui_done_callback):
    def load_thread():
      gui.Application.instance.post_to_main_thread(self.window, ui_done_callback)
    threading.Thread(target=load_thread).start()

  def _update_bounding_boxes(self):
    pass

  def _update_geometry(self):
    self._3d.force_redraw()

  def _init_user_interface(self, title, width, height):
    self.window = gui.Application.instance.create_window(title, width, height)
    self.window.set_on_layout(self._on_layout)

    em = self.window.theme.font_size

    self._3d = gui.SceneWidget()
    self._3d.enable_scene_caching(True)
    self._3d.scene = rendering.Open3DScene(self.window.renderer)
    self.window.add_child(self._3d)

    self._panel = gui.Vert()
    self.window.add_child(self._panel)

    indented_margins = gui.Margins(em, 0, em, 0)


  def _visualize(self, title, width, height):
    gui.Application.instance.initialize()
    self._init_user_interface(title, width, height)

    self._3d.scene.downsample_threshold = 400000

    def on_done_ui():
      self._update_bounding_boxes()
      self._update_geometry()
      self.setup_camera()

    self._load_geometries(self._objects.data_names, on_done_ui)

    gui.Application.instance.run()
