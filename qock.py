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


import sys
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from datetime import datetime
import time
from EPD import EPD

import pyowm
import owm_config

WHITE = 1
BLACK = 0

CLOCK_FONT_FILE = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
DATE_FONT_FILE = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
# WEEKDAY_FONT_FILE = '/home/pi/gulim.ttc'
WEEKDAY_FONT_FILE = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
NOW_WEATHER_FONT_FILE = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
DAY_WEATHER_FONT_FILE = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'

# fonts are in different places on Raspbian/Angstrom so search
possible_fonts = [
    CLOCK_FONT_FILE,
    DATE_FONT_FILE,
    WEEKDAY_FONT_FILE,
    NOW_WEATHER_FONT_FILE,
    DAY_WEATHER_FONT_FILE
]

for f in possible_fonts:
    if not os.path.exists(f):
        raise 'no font file found'


class Settings27(object):
    # fonts
    CLOCK_FONT_SIZE = 50
    DATE_FONT_SIZE = 22
    WEEKDAY_FONT_SIZE = 22
    NOW_WEATHER_FONT_SIZE = 20
    DAY_WEATHER_FONT_SIZE = 14

    # time
    X_OFFSET = 0
    Y_OFFSET = 15

    # date
    DATE_X = 8
    DATE_Y = -2

    # weekday
    WEEKDAY_X = 135
    WEEKDAY_Y = -2

    # now weather
    NOW_WEATHER_X = 0
    NOW_WEATHER_Y = 65

    # day weather
    DAY_WEATHER_X = 0
    DAY_WEATHER_Y = 90
    DAY_WEATHER_HEIGHT = 16


DAYS = [
    u"Mon",
    u"Tue",
    u"Wed",
    u"Thu",
    u"Fri",
    u"Sat",
    u"Sun"
]

daily_weather = [
]


def main(argv):
    """main program - draw HH:MM clock on 2.70" size panel"""

    global settings
    global owm
    epd = EPD()

    print(
        'panel = {p:s} {w:d} x {h:d}  version={v:s} COG={g:d} FILM={f:d}'.format(p=epd.panel, w=epd.width, h=epd.height,
                                                                                 v=epd.version, g=epd.cog, f=epd.film))

    if 'EPD 2.7' == epd.panel:
        settings = Settings27()
    else:
        print('incorrect panel size')
        sys.exit(1)

    epd.clear()

    owm = pyowm.OWM(owm_config.weather_api_key)

    demo(epd, settings)


def demo(epd, settings):
    """draw a clock"""

    # initially set all white background
    image = Image.new('1', epd.size, WHITE)

    # prepare for drawing
    draw = ImageDraw.Draw(image)
    width, height = image.size

    clock_font = ImageFont.truetype(CLOCK_FONT_FILE, settings.CLOCK_FONT_SIZE)
    date_font = ImageFont.truetype(DATE_FONT_FILE, settings.DATE_FONT_SIZE)
    weekday_font = ImageFont.truetype(WEEKDAY_FONT_FILE, settings.WEEKDAY_FONT_SIZE)
    now_weather_font = ImageFont.truetype(NOW_WEATHER_FONT_FILE, settings.NOW_WEATHER_FONT_SIZE)
    day_weather_font = ImageFont.truetype(DAY_WEATHER_FONT_FILE, settings.DAY_WEATHER_FONT_SIZE)

    # initial time
    now = datetime.today()

    refresh_minute = now.minute % 60

    while True:

        now = datetime.today()

        # clear the display buffer
        draw.rectangle((0, 0, width, height), fill=WHITE, outline=WHITE)

        # update weather

        if refresh_minute == now.minute:
            obs = owm.weather_at_place(owm_config.weather_location)
            w = obs.get_weather()
            now_weather_str = w.get_detailed_status()
            now_weather_str += ", "
            now_weather_str += str(w.get_temperature(unit='celsius')['temp'])
            now_weather_str += "'C, "
            now_weather_str += str(w.get_humidity())
            now_weather_str += "%"

            print("now_weather_str=" + now_weather_str)

            fc = owm.daily_forecast(owm_config.weather_location, limit=3)
            f = fc.get_forecast()
            lst = f.get_weathers()

            for weather in f:
                month = datetime.fromtimestamp(int(weather.get_reference_time())).month
                day = datetime.fromtimestamp(int(weather.get_reference_time())).day
                day_str = '{m:02d}/{d:02d} {status:s}'.format(m=month, d=day, status=weather.get_detailed_status())
                print(day_str)
                daily_weather.append(day_str)

        # hours
        draw.text((settings.X_OFFSET, settings.Y_OFFSET), '{h:02d}:{m:02d}'.format(h=now.hour, m=now.minute),
                  fill=BLACK, font=clock_font)
        # date
        draw.text((settings.DATE_X, settings.DATE_Y),
                  '{y:04d}/{m:02d}/{d:02d}'.format(y=now.year, m=now.month, d=now.day), fill=BLACK, font=date_font)
        # weekday
        draw.text((settings.WEEKDAY_X, settings.WEEKDAY_Y), u'{w:s}'.format(w=DAYS[now.weekday()]), fill=BLACK,
                  font=weekday_font)
        # now weather
        draw.text((settings.NOW_WEATHER_X, settings.NOW_WEATHER_Y), '{w:s}'.format(w=now_weather_str), fill=BLACK,
                  font=now_weather_font)

        # dayily weather
        i = 0
        for daily_weather_str in daily_weather:
            draw.text((settings.DAY_WEATHER_X, settings.DAY_WEATHER_Y + i * settings.DAY_WEATHER_HEIGHT),
                      '{w:s}'.format(w=daily_weather_str), fill=BLACK, font=day_weather_font)
            i = i + 1

        # display image on the panel
        epd.display(image)

        if now.minute % 30 == 0:
            epd.update()
        else:
            epd.partial_update()

        # wait for next minute
        while True:
            now = datetime.today()
            if now.second == 0:
                break
            time.sleep(0.5)


# main
if "__main__" == __name__:
    if len(sys.argv) < 1:
        sys.exit('usage: {p:s}'.format(p=sys.argv[0]))

    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit('interrupted')
        pass
