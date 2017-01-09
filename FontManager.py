# -*- coding: utf-8 -*-
# Copyright 2017 issess
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
