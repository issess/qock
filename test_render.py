# -*- coding: utf-8 -*-
import os
import sys

from PIL import Image, ImageDraw
from datetime import datetime

from FontManager import FontManager
from QockText import QockText
from QockFont import QockFont

try:
    import feedparser
except ImportError:
    sys.exit("feedparser not installed. Run: pip install feedparser")

WHITE = 1
BLACK = 0
WIDTH = 264
HEIGHT = 176


def wrap_text(text, font, max_width):
    lines = []
    current = ""
    for char in text:
        test = current + char
        if font.getlength(test) <= max_width:
            current = test
        else:
            lines.append(current)
            current = char
    if current:
        lines.append(current)
    return lines


def fetch_news(rss_url, count=3):
    try:
        feed = feedparser.parse(rss_url)
        headlines = []
        for entry in feed.entries[:count]:
            headlines.append(entry.title)
        return headlines
    except Exception as err:
        print("News fetch error: %s" % str(err))
        return [u"뉴스를 불러올 수 없습니다."]


def render_clock_screen(settings, draw, width, height):
    now = datetime.today()
    draw.rectangle((0, 0, width, height), fill=WHITE, outline=WHITE)

    settings['clock_text'].text = '{h:02d}:{m:02d}'.format(h=now.hour, m=now.minute)
    settings['clock_text'].render(draw)

    settings['date_text'].text = '{y:04d}/{m:02d}/{d:02d}'.format(y=now.year, m=now.month, d=now.day)
    settings['date_text'].render(draw)

    settings['weather_temp'].text = u"22.5°C"
    settings['weather_temp'].render(draw)

    settings['weather_icon'].text = "B"
    settings['weather_icon'].render(draw)

    sample_days = []
    for i in range(5):
        d = now.day + i + 1
        m = now.month
        sample_days.append((m, d))

    icons = ["B", "H", "R", "N", "Q"]
    temps = [u"15/22", u"13/20", u"10/18", u"14/21", u"12/19"]

    for i in range(5):
        m, d = sample_days[i]
        settings['day_text'][i].text = '{m:02d}/{d:02d}'.format(m=m, d=d)
        settings['day_icon'][i].text = icons[i]
        settings['day_temp'][i].text = temps[i]
        settings['day_text'][i].render(draw)
        settings['day_icon'][i].render(draw)
        settings['day_temp'][i].render(draw)


def render_news_screen(settings, draw, width, height, headlines):
    draw.rectangle((0, 0, width, height), fill=WHITE, outline=WHITE)

    settings['news_title'].text = u"뉴스"
    settings['news_title'].render(draw)

    line_idx = 0
    max_width = width - 20
    font_obj = settings['font12'].font
    for headline in headlines:
        wrapped = wrap_text(headline, font_obj, max_width)
        for line in wrapped[:2]:
            if line_idx < len(settings['news_line']):
                settings['news_line'][line_idx].text = line
                settings['news_line'][line_idx].render(draw)
                line_idx += 1


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

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

    settings = {
        'font12': font12,
        'clock_text': QockText("clock_text", font45, 20, 20),
        'date_text': QockText("date_text", font22, 20, 70),
        'weather_icon': QockText("now_weather_icon", font80, 160, 0),
        'weather_temp': QockText("now_weather_temp", font20, 170, 80),
        'day_text': [],
        'day_icon': [],
        'day_temp': [],
        'news_title': QockText("news_title", font20, 10, 5),
        'news_line': [],
    }

    for i in range(5):
        settings['day_text'].append(QockText("day_weather_text_%d" % i, font9, 10 + i * 52, 115))
        settings['day_icon'].append(QockText("day_weather_icon_%d" % i, font30, 10 + i * 52, 132))
        settings['day_temp'].append(QockText("day_weather_temp_%d" % i, font12, 10 + i * 52, 162))

    for i in range(6):
        settings['news_line'].append(QockText("news_line_%d" % i, font12, 10, 35 + i * 23))

    # render clock screen
    image1 = Image.new('1', (WIDTH, HEIGHT), WHITE)
    draw1 = ImageDraw.Draw(image1)
    render_clock_screen(settings, draw1, WIDTH, HEIGHT)
    image1_rgb = image1.convert('RGB')
    image1_rgb.save('test_clock.jpg', 'JPEG', quality=95)
    print("Saved: test_clock.jpg")

    # render news screen
    rss_url = 'https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko'
    if os.path.isfile('news_config.py'):
        import news_config
        rss_url = news_config.news_rss_url

    print("Fetching news from: %s" % rss_url)
    headlines = fetch_news(rss_url, count=3)
    for i, h in enumerate(headlines):
        print("  [%d] %s" % (i, h))

    image2 = Image.new('1', (WIDTH, HEIGHT), WHITE)
    draw2 = ImageDraw.Draw(image2)
    render_news_screen(settings, draw2, WIDTH, HEIGHT, headlines)
    image2_rgb = image2.convert('RGB')
    image2_rgb.save('test_news.jpg', 'JPEG', quality=95)
    print("Saved: test_news.jpg")


if __name__ == '__main__':
    main()
