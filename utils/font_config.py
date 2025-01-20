import matplotlib.pyplot as plt
import os
import matplotlib.font_manager as fm

def set_korean_font():
    plt.rcParams["axes.unicode_minus"] = False
    font_path = "C:/Windows/Fonts/malgun.ttf" if os.name == "nt" else "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
    if os.path.exists(font_path):
        font = fm.FontProperties(fname=font_path)
        plt.rc("font", family=font.get_name())
