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
import sys
import random

from PIL import Image
from PIL import ImageDraw
from datetime import datetime, timedelta
import time
from EPD import EPD
import socket
import logging

import pyowm
import owm_config

from FontManager import FontManager
from QockText import QockText

import RPi.GPIO as GPIO  # Use the python GPIO handler for RPi

GPIO.setmode(GPIO.BCM)  # Use the Broadcom GPIO pin designations
GPIO.setwarnings(False)

WHITE = 1
BLACK = 0

logger = logging.getLogger("DaemonLog")

iconmap = {"01d": "B", "01n": "C",  # clear sky
           "02d": "H", "02n": "I",  # few clouds
           "03d": "N", "03n": "N",  # scattered clouds
           "04d": "Y", "04n": "Y",  # broken clouds
           "09d": "Q", "09n": "Q",  # shower rain
           "10d": "R", "10n": "R",  # rain
           "11d": "0", "11n": "0",  # thunderstorm
           "13d": "W", "13n": "W",  # snow
           "50d": "J", "50n": "K",  # mist
           }


class Settings27(object):
    clock_text = QockText("clock_text", 20, 20, 45)
    date_text = QockText("date_text", 20, 70, 22)
    weekday_text = QockText("weekday_text", 135, 0, 45)

    now_weather_icon = QockText("now_weather_icon", 150, 0, 100)
    now_weather_temp = QockText("now_weather_temp", 170, 90, 20)

    day_weather_text = QockText("day_weather_text", 10, 115, 9)
    day_weather_icon = QockText("day_weather_icon", 10, 132, 30)
    day_weather_temp = QockText("day_weather_temp", 10, 162, 12)

    fontManager = FontManager()


DAYS = [
    u"월요일",
    u"화요일",
    u"수요일",
    u"목요일",
    u"금요일",
    u"토요일",
    u"일요일"
]

menu = {"menu": "메뉴"}


def my_callback(channel):  # When a button is pressed, report which channel and flash led
    logger.debug("Falling edge detected on port %s" % channel)
    flash_led(channel)


def flash_led(channel):
    if (channel == 16):
        GPIO.output(6, 1)  # flash red on GPIO6
        time.sleep(0.01)
        GPIO.output(6, 0)
    elif (channel == 19):
        GPIO.output(12, 1)  # flash green on GPIO12
        time.sleep(0.01)
        GPIO.output(12, 0)
    elif (channel == 20):
        GPIO.output(5, 1)  # flash blue on GPIO5
        time.sleep(0.01)
        GPIO.output(5, 0)
    elif (channel == 26):
        GPIO.output(12, 1)  # flash them all
        GPIO.output(6, 1)
        GPIO.output(5, 1)
        time.sleep(0.01)
        GPIO.output(12, 0)
        GPIO.output(6, 0)
        GPIO.output(5, 0)


def main(argv):
    main_program()


def main_program():
    """main program - draw HH:MM clock on 2.70" size panel"""
    global settings
    global owm

    while True:
        if os.path.isfile("/dev/epd/version"):
            print "epd..ok!"
            break
        else:
            print "epd init.."
            time.sleep(1)

    logger.debug("qock start!")
    logger.debug("current path="+str(os.getcwd()))

    epd = EPD()

    logger.debug('panel = {p:s} {w:d} x {h:d}  version={v:s} COG={g:d} FILM={f:d}'.format(
        p=epd.panel, w=epd.width, h=epd.height, v=epd.version, g=epd.cog, f=epd.film))

    if 'EPD 2.7' == epd.panel:
        settings = Settings27()
    else:
        logger.debug('incorrect panel size')
        sys.exit(1)

    epd.clear()

    owm = pyowm.OWM(owm_config.weather_api_key)

    initGPIO()
    loop(epd, settings)


def initGPIO():
    for channel in [5, 6, 12]:
        GPIO.setup(channel, GPIO.OUT)
        GPIO.output(channel, 0)

    # Buttons are on GPIO16, 19, 20 & 26 left to right
    for channel in [16, 19, 20, 26]:
        # Set buttons as input with internal pull-up
        GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # Event detect a button press, falling edge - switched to ground
        # On detect, do actions in my_callback function, switch debounce of 500ms
        GPIO.add_event_detect(channel, GPIO.FALLING, callback=my_callback, bouncetime=500)


def utc2local(utc):
    epoch = time.mktime(utc.timetuple())
    offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(epoch)
    return utc + offset


def loop(epd, settings):
    # initially set all white background

    daily_weather = []
    daily_weather_icon = []
    daily_weather_temp = []

    image = Image.new('1', epd.size, WHITE)

    logger.debug("load font...")

    settings.clock_text.loadFont(settings.fontManager.getDefaultFontPath())
    settings.date_text.loadFont(settings.fontManager.getDefaultFontPath())
    settings.weekday_text.loadFont(settings.fontManager.getDefaultFontPath())

    settings.now_weather_icon.loadFont(settings.fontManager.getWeatherFontPath())
    settings.now_weather_temp.loadFont(settings.fontManager.getDefaultFontPath())

    settings.day_weather_text.loadFont(settings.fontManager.getDefaultFontPath())
    settings.day_weather_icon.loadFont(settings.fontManager.getWeatherFontPath())
    settings.day_weather_temp.loadFont(settings.fontManager.getDefaultFontPath())

    # prepare for drawing
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # initial time
    now = datetime.today()

    refresh_minute = now.minute % 60

    logger.debug("loop start...")
    while True:

        now = datetime.today()

        # clear the display buffer
        draw.rectangle((0, 0, width, height), fill=WHITE, outline=WHITE)

        # update weather
        if refresh_minute == now.minute:
            try:
                obs = owm.weather_at_place(owm_config.weather_location)
                w = obs.get_weather()

                settings.now_weather_temp.text = u"{temp:02.1f}°C".format(
                    temp=w.get_temperature(unit='celsius')['temp'])
                settings.now_weather_icon.text = iconmap.get(w.get_weather_icon_name(), ")")
                fc = owm.daily_forecast(owm_config.weather_location, limit=5)
                f = fc.get_forecast()
                lst = f.get_weathers()
            except Exception as err:
                logger.debug(str(err))
                settings.now_weather_temp.text = u"?? °C"
                settings.now_weather_icon.text = ")"
                f = []
                refresh_minute = (now.minute + 1) % 60  # try againddd

            # now_weather_str += str(w.get_humidity())
            # now_weather_str += "%, "
            # now_weather_str += str(w.get_wind()['speed'])
            # now_weather_str += "m/s"
            # logger.debug("now_weather_str=" + temp_str + " now_weather_icon_str=" + now_weather_icon_str)

            if len(f) > 0:
                daily_weather = []
                daily_weather_icon = []
                daily_weather_temp = []
                timegap = now.utcnow() - (
                    datetime.fromtimestamp(int(f.get(0).get_reference_time())) - timedelta(hours=12))

                for weather in f:
                    logger.debug("=======================")
                    utcdaytime = datetime.fromtimestamp(int(weather.get_reference_time())) - timedelta(hours=12)
                    daytime = utc2local(utcdaytime + timegap)

                    month = datetime.fromtimestamp(int(weather.get_reference_time())).month
                    day = datetime.fromtimestamp(int(weather.get_reference_time())).day
                    hour = datetime.fromtimestamp(int(weather.get_reference_time())).hour
                    minute = datetime.fromtimestamp(int(weather.get_reference_time())).minute
                    second = datetime.fromtimestamp(int(weather.get_reference_time())).second

                    logger.debug("month=" + str(month) + " day=" + str(day) + " hour=" + str(hour) + " minute=" + str(
                        minute) + " second=" + str(second))

                    month = daytime.month
                    day = daytime.day
                    hour = daytime.hour
                    minute = daytime.minute
                    second = daytime.second

                    logger.debug("month=" + str(month) + " day=" + str(day) + " hour=" + str(hour) + " minute=" + str(
                        minute) + " second=" + str(second))

                    # logger.debug "utcdaytime=" + str(utcdaytime)
                    # logger.debug "daytime=" + str(daytime)

                    month = daytime.month
                    day = daytime.day
                    day_str = '{m:02d}/{d:02d}'.format(m=month, d=day)
                    daily_weather.append(day_str)
                    daily_weather_icon.append(iconmap.get(weather.get_weather_icon_name(), ")"))
                    daily_weather_temp.append(
                        u"{min:2.0f}/{max:2.0f}".format(min=weather.get_temperature(unit='celsius')['min'],
                                                        max=weather.get_temperature(unit='celsius')['max']))
                    logger.debug(day_str + " " + iconmap.get(weather.get_weather_icon_name(),
                                                             ")") + " " + weather.get_weather_icon_name() + " " + weather.get_status() + "(" + weather.get_detailed_status() + ")")
            else:
                logger.debug("size 0")

        # hours
        draw.text((settings.clock_text.x, settings.clock_text.y), '{h:02d}:{m:02d}'.format(h=now.hour, m=now.minute),
                  fill=BLACK, font=settings.clock_text.font)

        # date
        draw.text((settings.date_text.x, settings.date_text.y),
                  '{y:04d}/{m:02d}/{d:02d}'.format(y=now.year, m=now.month, d=now.day), fill=BLACK,
                  font=settings.date_text.font)

        # weekday
        # draw.text((settings.WEEKDAY_X, settings.WEEKDAY_Y), u'{w:s}'.format(w=DAYS[now.weekday()]), fill=BLACK, font=weekday_font)

        # now weather temp
        settings.now_weather_temp.render(draw)

        # now weather icon
        settings.now_weather_icon.render(draw)

        # daily weather
        i = 0
        for daily_weather_str in daily_weather:
            draw.text((settings.day_weather_text.x + i * 52, settings.day_weather_text.y),
                      '{w:s}'.format(w=daily_weather_str),
                      fill=BLACK, font=settings.day_weather_text.font)
            i = i + 1

        # daily icon
        i = 0
        for daily_weather_icon_str in daily_weather_icon:
            draw.text((settings.day_weather_icon.x + i * 52, settings.day_weather_icon.y),
                      '{w:s}'.format(w=daily_weather_icon_str), fill=BLACK, font=settings.day_weather_icon.font)
            i = i + 1

        # daily temp
        i = 0
        for daily_weather_temp_str in daily_weather_temp:
            draw.text((settings.day_weather_temp.x + i * 52, settings.day_weather_temp.y),
                      u'{w:s}'.format(w=daily_weather_temp_str), fill=BLACK, font=settings.day_weather_temp.font)
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
        GPIO.cleanup()  # Clean up when exiting with Ctrl-C
        logger.debug("Cleaning up!")
        pass
