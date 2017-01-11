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

import os


#############################################
# FONT Manager
#############################################

class FontManager(object):
    font_path = {}

    def __init__(self):
        self.initFont();

    def getFontFiles(self, type):
        possible_fonts_files = []
        path = os.path.join("fonts", type)
        font_dirs = os.listdir(path)
        for font_dir in font_dirs:
            font_files = os.listdir(os.path.join(path, font_dir))
            for font_file in font_files:
                ext = os.path.splitext(font_file)[-1]
                if ext == '.ttf' or ext == '.TTF':
                    possible_fonts_files.append(os.path.join(path, font_dir, font_file))
        return possible_fonts_files

    def initFont(self):
        self.font_path = {}
        self.font_path["text"] = self.getFontFiles("text")
        self.font_path["weather"] = self.getFontFiles("weather")
        self.font_path["default"] = self.getFontFiles("default")

        for k, v in self.font_path.items():
            if len(v) == 0:
                raise str(k) + ': no font file found'

        self.font = {}
        self.font["text"] = {}
        self.font["default"] = {}
        self.font["weather"] = {}

    def getTextFontPath(self, i):
        return self.font_path["text"][i]

    def getDefaultFontPath(self):
        return self.font_path["default"][0]

    def getWeatherFontPath(self):
        return self.font_path["weather"][0]
