# -*- coding: utf-8 -*-
# The MIT License (MIT)
#
# Copyright (c) 2016 SeungHoon Han (issess)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from QockObject import QockObject

from PIL import ImageFont

WHITE = 1
BLACK = 0


class QockFont(QockObject):
    def __init__(self, name, path, font_size):
        QockObject.__init__(self, name)
        self._font_size = font_size
        self._path = path
        self._font = ImageFont.truetype(path, self._font_size)

    def __str__(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def font(self):
        return self._font

    @property
    def font_size(self):
        return self._font_size
