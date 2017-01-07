
import os

#############################################
# FONT
#############################################

def getFontFiles(type):
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


def initFont():
    possible_fonts = {}
    possible_fonts["text"] = getFontFiles("text")
    possible_fonts["weather"] = getFontFiles("weather")
    possible_fonts["default"] = getFontFiles("default")

    for k, v in possible_fonts.items():
        print "init " + str(k) + " " + str(len(v))
        if len(v) == 0:
            raise str(k) + ': no font file found'

    return possible_fonts
