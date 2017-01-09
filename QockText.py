# -*- coding: utf-8 -*-
# Copyright 2013-2015 Pervasive Displays, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.  See the License for the specific language
# governing permissions and limitations under the License.

from QockObject import QockObject

from PIL import ImageFont


class QockText(QockObject):
    def __init__(self, name, x=0, y=0, font_size=0):
        self._name = name
        self._x = x
        self._y = y
        self._font_size = font_size

    def __str__(self):
        return self._name

    def loadFont(self, path):
        self._font = ImageFont.truetype(path, self._font_size)

    @property
    def font(self):
        return self._font

    @property
    def text(self):
        return self._text

    @property
    def font_size(self):
        return self._font_size
