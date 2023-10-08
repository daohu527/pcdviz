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

import math
import numpy as np

COLOR_MAP = {
    "red": [1, 0, 0],
    "yellow": [0, 1, 0],
    "blue": [0, 0, 1],
    "black": [0, 0, 0]
}


def euler_to_rotation_matrix(theta1, theta2, theta3, order='xyz'):
    c1 = np.cos(theta1)
    s1 = np.sin(theta1)
    c2 = np.cos(theta2)
    s2 = np.sin(theta2)
    c3 = np.cos(theta3)
    s3 = np.sin(theta3)

    if order == 'xzx':
        matrix = np.array([[c2, -c3*s2, s2*s3],
                           [c1*s2, c1*c2*c3-s1*s3, -c3*s1-c1*c2*s3],
                           [s1*s2, c1*s3+c2*c3*s1, c1*c3-c2*s1*s3]])
    elif order == 'xyx':
        matrix = np.array([[c2, s2*s3, c3*s2],
                           [s1*s2, c1*c3-c2*s1*s3, -c1*s3-c2*c3*s1],
                           [-c1*s2, c3*s1+c1*c2*s3, c1*c2*c3-s1*s3]])
    elif order == 'yxy':
        matrix = np.array([[c1*c3-c2*s1*s3, s1*s2, c1*s3+c2*c3*s1],
                           [s2*s3, c2, -c3*s2],
                           [-c3*s1-c1*c2*s3, c1*s2, c1*c2*c3-s1*s3]])
    elif order == 'yzy':
        matrix = np.array([[c1*c2*c3-s1*s3, -c1*s2, c3*s1+c1*c2*s3],
                          [c3*s2, c2, s2*s3],
                          [-c1*s3-c2*c3*s1, s1*s2, c1*c3-c2*s1*s3]])
    elif order == 'zyz':
        matrix = np.array([[c1*c2*c3-s1*s3, -c3*s1-c1*c2*s3, c1*s2],
                          [c1*s3+c2*c3*s1, c1*c3-c2*s1*s3, s1*s2],
                          [-c3*s2, s2*s3, c2]])
    elif order == 'zxz':
        matrix = np.array([[c1*c3-c2*s1*s3, -c1*s3-c2*c3*s1, s1*s2],
                          [c3*s1+c1*c2*s3, c1*c2*c3-s1*s3, -c1*s2],
                          [s2*s3, c3*s2, c2]])
    elif order == 'xyz':
        matrix = np.array([[c2*c3, -c2*s3, s2],
                          [c1*s3+c3*s1*s2, c1*c3-s1*s2*s3, -c2*s1],
                          [s1*s3-c1*c3*s2, c3*s1+c1*s2*s3, c1*c2]])
    elif order == 'xzy':
        matrix = np.array([[c2*c3, -s2, c2*s3],
                          [s1*s3+c1*c3*s2, c1*c2, c1*s2*s3-c3*s1],
                          [c3*s1*s2-c1*s3, c2*s1, c1*c3+s1*s2*s3]])
    elif order == 'yxz':
        matrix = np.array([[c1*c3+s1*s2*s3, c3*s1*s2-c1*s3, c2*s1],
                          [c2*s3, c2*c3, -s2],
                          [c1*s2*s3-c3*s1, c1*c3*s2+s1*s3, c1*c2]])
    elif order == 'yzx':
        matrix = np.array([[c1*c2, s1*s3-c1*c3*s2, c3*s1+c1*s2*s3],
                          [s2, c2*c3, -c2*s3],
                          [-c2*s1, c1*s3+c3*s1*s2, c1*c3-s1*s2*s3]])
    elif order == 'zyx':
        matrix = np.array([[c1*c2, c1*s2*s3-c3*s1, s1*s3+c1*c3*s2],
                          [c2*s1, c1*c3+s1*s2*s3, c3*s1*s2-c1*s3],
                          [-s2, c2*s3, c2*c3]])
    elif order == 'zxy':
        matrix = np.array([[c1*c3-s1*s2*s3, -c2*s1, c1*s3+c3*s1*s2],
                          [c3*s1+c1*s2*s3, c1*c2, s1*s3-c1*c3*s2],
                          [-c2*s3, s2, c2*c3]])
    return matrix


def is_rotation_matrix(R):
    Rt = np.transpose(R)
    should_be_identity = np.dot(Rt, R)
    I = np.identity(3, dtype=R.dtype)
    n = np.linalg.norm(I - should_be_identity)
    return n < 1e-6


def rotation_matrix_to_euler(R):
    assert (is_rotation_matrix(R))
    sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
    singular = sy < 1e-6
    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0
    return np.array([x, y, z])
