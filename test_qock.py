# -*- coding: utf-8 -*-
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Mock hardware-dependent modules before importing Qock
sys.modules['RPi'] = MagicMock()
sys.modules['RPi.GPIO'] = MagicMock()
sys.modules['pyowm'] = MagicMock()
sys.modules['owm_config'] = MagicMock()
sys.modules['news_config'] = MagicMock(
    news_rss_url='http://example.com/rss',
    news_refresh_minutes=30,
    screen_rotate_seconds=30,
)

from PIL import Image, ImageDraw, ImageFont

from FontManager import FontManager
from QockText import QockText
from QockFont import QockFont
from QockContainer import QockContainer
from QockObject import QockObject
from Qock import fetch_news, wrap_text

WHITE = 1
BLACK = 0
WIDTH = 264
HEIGHT = 176


class TestWrapText(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        fm = FontManager()
        cls.font = ImageFont.truetype(fm.getDefaultFontPath(), 12)

    def test_short_text_single_line(self):
        result = wrap_text("Hello", self.font, WIDTH)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "Hello")

    def test_empty_text(self):
        result = wrap_text("", self.font, WIDTH)
        self.assertEqual(result, [])

    def test_long_text_wraps(self):
        long_text = u"이것은 매우 긴 텍스트입니다. 화면 폭을 초과하여 여러 줄로 나뉘어야 합니다."
        result = wrap_text(long_text, self.font, WIDTH - 20)
        self.assertGreater(len(result), 1)
        self.assertEqual("".join(result), long_text)

    def test_all_chars_preserved(self):
        text = u"ABC가나다123"
        result = wrap_text(text, self.font, WIDTH)
        self.assertEqual("".join(result), text)

    def test_narrow_width_wraps_every_char(self):
        result = wrap_text("ABCD", self.font, 1)
        # width=1 is narrower than any single char, so each char becomes its own line
        # with a leading empty string from the first overflow
        self.assertEqual("".join(result), "ABCD")
        self.assertGreaterEqual(len(result), 4)


class TestFetchNews(unittest.TestCase):

    @patch('Qock.feedparser.parse')
    def test_returns_headlines(self, mock_parse):
        mock_parse.return_value = MagicMock(
            entries=[
                MagicMock(title=u"뉴스 제목 1"),
                MagicMock(title=u"뉴스 제목 2"),
                MagicMock(title=u"뉴스 제목 3"),
            ]
        )
        result = fetch_news("http://example.com/rss", count=3)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], u"뉴스 제목 1")

    @patch('Qock.feedparser.parse')
    def test_count_limits_results(self, mock_parse):
        mock_parse.return_value = MagicMock(
            entries=[
                MagicMock(title="A"),
                MagicMock(title="B"),
                MagicMock(title="C"),
            ]
        )
        result = fetch_news("http://example.com/rss", count=2)
        self.assertEqual(len(result), 2)

    @patch('Qock.feedparser.parse')
    def test_empty_feed(self, mock_parse):
        mock_parse.return_value = MagicMock(entries=[])
        result = fetch_news("http://example.com/rss", count=3)
        self.assertEqual(result, [])

    @patch('Qock.feedparser.parse', side_effect=Exception("network error"))
    def test_exception_returns_fallback(self, mock_parse):
        result = fetch_news("http://example.com/rss")
        self.assertEqual(len(result), 1)
        self.assertIn(u"뉴스를 불러올 수 없습니다", result[0])


class TestFontManager(unittest.TestCase):

    def setUp(self):
        self.fm = FontManager()

    def test_default_font_exists(self):
        path = self.fm.getDefaultFontPath()
        self.assertTrue(os.path.isfile(path))

    def test_weather_font_exists(self):
        path = self.fm.getWeatherFontPath()
        self.assertTrue(os.path.isfile(path))

    def test_font_path_is_ttf(self):
        path = self.fm.getDefaultFontPath()
        self.assertTrue(path.lower().endswith('.ttf'))


class TestQockFont(unittest.TestCase):

    def setUp(self):
        fm = FontManager()
        self.qf = QockFont("test_font", fm.getDefaultFontPath(), 20)

    def test_font_size(self):
        self.assertEqual(self.qf.font_size, 20)

    def test_font_is_truetype(self):
        self.assertIsInstance(self.qf.font, ImageFont.FreeTypeFont)

    def test_path_stored(self):
        self.assertTrue(self.qf.path.endswith('.ttf'))


class TestQockText(unittest.TestCase):

    def setUp(self):
        fm = FontManager()
        qf = QockFont("test_font", fm.getDefaultFontPath(), 12)
        self.qt = QockText("test_text", qf, 10, 20)

    def test_position(self):
        self.assertEqual(self.qt.x, 10)
        self.assertEqual(self.qt.y, 20)

    def test_set_text(self):
        self.qt.text = u"테스트"
        self.assertEqual(self.qt.text, u"테스트")

    def test_render_no_error(self):
        image = Image.new('1', (WIDTH, HEIGHT), WHITE)
        draw = ImageDraw.Draw(image)
        self.qt.text = u"Hello"
        self.qt.render(draw)


class TestQockContainer(unittest.TestCase):

    def test_append_and_count(self):
        container = QockContainer("test_container")
        container.childs = []
        fm = FontManager()
        qf = QockFont("f", fm.getDefaultFontPath(), 12)
        t1 = QockText("t1", qf, 0, 0)
        t2 = QockText("t2", qf, 0, 0)
        container.append(t1)
        container.append(t2)
        self.assertEqual(len(container.childs), 2)

    def test_remove(self):
        container = QockContainer("test_container")
        container.childs = []
        fm = FontManager()
        qf = QockFont("f", fm.getDefaultFontPath(), 12)
        t1 = QockText("t1", qf, 0, 0)
        container.append(t1)
        container.remove(t1)
        self.assertEqual(len(container.childs), 0)


class TestSettings27Layout(unittest.TestCase):

    def test_news_elements_exist(self):
        from Qock import Settings27
        s = Settings27()
        self.assertIsNotNone(s.news_title)
        self.assertEqual(len(s.news_line), 6)

    def test_news_line_positions(self):
        from Qock import Settings27
        s = Settings27()
        for i in range(6):
            expected_y = 35 + i * 23
            self.assertEqual(s.news_line[i].y, expected_y)

    def test_clock_elements_exist(self):
        from Qock import Settings27
        s = Settings27()
        self.assertIsNotNone(s.clock_text)
        self.assertIsNotNone(s.date_text)
        self.assertIsNotNone(s.now_weather_icon)
        self.assertIsNotNone(s.now_weather_temp)

    def test_day_weather_count(self):
        from Qock import Settings27
        s = Settings27()
        self.assertEqual(len(s.day_weather_text), 5)
        self.assertEqual(len(s.day_weather_icon), 5)
        self.assertEqual(len(s.day_weather_temp), 5)


class TestRenderScreens(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from Qock import Settings27
        cls.settings = Settings27()

    def test_clock_screen_renders(self):
        image = Image.new('1', (WIDTH, HEIGHT), WHITE)
        draw = ImageDraw.Draw(image)

        self.settings.clock_text.text = '12:34'
        self.settings.clock_text.render(draw)
        self.settings.date_text.text = '2026/03/14'
        self.settings.date_text.render(draw)
        self.settings.now_weather_temp.text = u"22.5°C"
        self.settings.now_weather_temp.render(draw)

        pixels = list(image.getdata())
        black_count = pixels.count(0)
        self.assertGreater(black_count, 0)

    def test_news_screen_renders(self):
        image = Image.new('1', (WIDTH, HEIGHT), WHITE)
        draw = ImageDraw.Draw(image)

        self.settings.news_title.text = u"뉴스"
        self.settings.news_title.render(draw)

        headlines = [u"테스트 뉴스 헤드라인 1", u"테스트 뉴스 헤드라인 2"]
        font_obj = self.settings.font12.font
        line_idx = 0
        for headline in headlines:
            wrapped = wrap_text(headline, font_obj, WIDTH - 20)
            for line in wrapped[:2]:
                if line_idx < len(self.settings.news_line):
                    self.settings.news_line[line_idx].text = line
                    self.settings.news_line[line_idx].render(draw)
                    line_idx += 1

        pixels = list(image.getdata())
        black_count = pixels.count(0)
        self.assertGreater(black_count, 0)

    def test_news_screen_blank_when_no_headlines(self):
        image = Image.new('1', (WIDTH, HEIGHT), WHITE)
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, WIDTH, HEIGHT), fill=WHITE, outline=WHITE)

        self.settings.news_title.text = u"뉴스"
        self.settings.news_title.render(draw)

        # no headlines rendered — only title has pixels
        pixels = list(image.getdata())
        black_count = pixels.count(0)
        self.assertGreater(black_count, 0)


if __name__ == '__main__':
    unittest.main()
