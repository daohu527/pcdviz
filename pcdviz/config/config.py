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

import yaml


class Config:
    def __init__(self, config_path) -> None:
        self.config_path = config_path
        self.parse(config_path)

    def parse(self, config_path):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

    @property
    def inputs(self):
        return self.config.get('inputs')

    @property
    def dataset(self):
        return self.config.get('dataset')

    @property
    def filters(self):
        return self.config.get('filters')

    @property
    def bounding_box(self):
        for input in self.config.get('inputs'):
            if input.get("name") == "bounding_box":
                return input
