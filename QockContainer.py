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

class QockObject(object):
    childs = []

    def __init__(self, name):
        self.name = name

    def append(self, qock):
        self.childs.add(qock)

    def remove(self, qock):
        self.childs.remove(qock)

    def __str__(self):
        return self.name

    def render(self, draw):
        for child in self.childs:
            child.render(draw)

    def update(self):
        for child in self.childs:
            child.update()
