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

from PIL import Image
from PIL import ImageDraw
from datetime import datetime, timedelta
import time
from EPD import EPD
import logging

import pyowm
import owm_config

from FontManager import FontManager
from QockText import QockText
from QockFont import QockFont
from QockContainer import QockContainer

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

root = QockContainer("root")


class Settings27(object):
    fontManager = FontManager()
    defaultTextFontPath = fontManager.getDefaultFontPath()
    defaultWeatherFontPath = fontManager.getWeatherFontPath()
    font80 = QockFont("weather_font_80", defaultWeatherFontPath, 80)
    font45 = QockFont("default_font_45", defaultTextFontPath, 45)
    font30 = QockFont("weather_font_30", defaultWeatherFontPath, 30)
    font22 = QockFont("default_font_22", defaultTextFontPath, 22)
    font20 = QockFont("default_font_20", defaultTextFontPath, 20)
    font12 = QockFont("default_font_12", defaultTextFontPath, 12)
    font9 = QockFont("default_font_9", defaultTextFontPath, 9)

    clock_text = QockText("clock_text", font45, 20, 20)
    date_text = QockText("date_text", font22, 20, 70)
    weekday_text = QockText("weekday_text", font45, 135, 0)

    now_weather_icon = QockText("now_weather_icon", font80, 160, 0)
    now_weather_temp = QockText("now_weather_temp", font20, 170, 80)

    day_weather_text = []
    day_weather_icon = []
    day_weather_temp = []

    for i in range(0, 5):
        day_weather_text.append(QockText("day_weather_text_%d" % i, font9, 10 + i * 52, 115))
        day_weather_icon.append(QockText("day_weather_icon_%d" % i, font30, 10 + i * 52, 132))
        day_weather_temp.append(QockText("day_weather_temp_%d" % i, font12, 10 + i * 52, 162))


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

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    while True:
        if os.path.isfile("/dev/epd/version"):
            logger.debug("epd..ok!")
            break
        else:
            logger.debug("epd init..")
            time.sleep(1)

    logger.debug("qock start!")
    logger.debug("current path=" + str(os.getcwd()))

    epd = EPD()

    logger.debug('panel={p:s} width={w:d} height={h:d} version={v:s} COG={g:d} FILM={f:d}'.format(
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
    image = Image.new('1', epd.size, WHITE)

    logger.debug("load font...")

    # prepare for drawing
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # initial time
    now = datetime.today()

    refresh_minute = now.minute % 60

    logger.debug("loop start...")

    # clear the display buffer

    while True:

        now = datetime.today()

        # clear the display buffer
        draw.rectangle((0, 0, width, height), fill=WHITE, outline=WHITE)

        # update weather
        if refresh_minute == now.minute:
            try:
                obs = owm.weather_at_place(owm_config.weather_location)
                w = obs.get_weather()

                settings.now_weather_temp.text = u"{temp:02.1f}°C".format(temp=w.get_temperature(unit='celsius')['temp'])
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
                timegap = now.utcnow() - (
                    datetime.fromtimestamp(int(f.get(0).get_reference_time())) - timedelta(hours=12))
                i = 0
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

                    settings.day_weather_text[i].text = '{m:02d}/{d:02d}'.format(m=daytime.month, d=daytime.day)
                    settings.day_weather_icon[i].text = iconmap.get(weather.get_weather_icon_name(), ")")
                    settings.day_weather_temp[i].text = u"{min:2.0f}/{max:2.0f}".format(
                        min=weather.get_temperature(unit='celsius')['min'],
                        max=weather.get_temperature(unit='celsius')['max'])
                    logger.debug("[" + str(i) + "] " + settings.day_weather_text[i].text + " " +
                                 iconmap.get(weather.get_weather_icon_name(), ")") + " " +
                                 weather.get_weather_icon_name() + " " +
                                 weather.get_status() + "(" + weather.get_detailed_status() + ")")
                    i = i + 1

            else:
                logger.debug("size 0")

        # hours
        settings.clock_text.text = '{h:02d}:{m:02d}'.format(h=now.hour, m=now.minute)
        settings.clock_text.render(draw)

        # date
        settings.date_text.text = '{y:04d}/{m:02d}/{d:02d}'.format(y=now.year, m=now.month, d=now.day)
        settings.date_text.render(draw)

        # now weather temp
        settings.now_weather_temp.render(draw)

        # now weather icon
        settings.now_weather_icon.render(draw)

        # daily weather
        for i in range(0, 5):
            settings.day_weather_temp[i].render(draw)
            settings.day_weather_icon[i].render(draw)
            settings.day_weather_text[i].render(draw)

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
