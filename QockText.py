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


class QockText(QockObject):
    def __init__(self, name, qock_font, x=0, y=0):
        QockObject.__init__(self, name)
        self._x = x
        self._y = y
        self._qock_font = qock_font
        self._text = ""

    def __str__(self):
        return self._name

    def render(self, draw):
        draw.text((self.x, self.y), u'{w:s}'.format(w=self._text), fill=BLACK, font=self._qock_font.font)

    @property
    def qock_font(self):
        return self._qock_font

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
