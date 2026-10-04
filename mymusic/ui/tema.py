"""Warna, font, dan stylesheet (QSS) seluruh aplikasi — diambil dari prototipe tahap 4."""
from PySide6.QtGui import QFontDatabase

from mymusic.config import AKSEN, FOLDER_FONT

LATAR = "#000000"  # jendela, bilah atas, bilah pemutar
PANEL = "#121212"  # koleksi, konten tengah, panel kanan
HOVER = "#1F1F1F"  # baris/kartu saat disorot, kotak cari
TERPILIH = "#2A2A2A"  # item aktif, chip
MENU = "#282828"
TEKS = "#FFFFFF"
TEKS_REDUP = "#A7A7A7"
TEKS_DI_AKSEN = "#111111"

NAMA_FONT = "Plus Jakarta Sans"
FONT_CADANGAN = "Segoe UI"


def muat_font():
    """Mendaftarkan file .ttf di aset/font. Mengembalikan nama font yang bisa dipakai."""
    for file in sorted(FOLDER_FONT.glob("*.ttf")):
        QFontDatabase.addApplicationFont(str(file))
    return NAMA_FONT if NAMA_FONT in QFontDatabase.families() else FONT_CADANGAN


def stylesheet(font):
    return f"""
    * {{ font-family: "{font}"; }}
    QWidget {{ color: {TEKS}; font-size: 14px; }}
    QMainWindow, #wadah {{ background: {LATAR}; }}
    #panel {{ background: {PANEL}; border-radius: 8px; }}
    QToolTip {{ background: {MENU}; color: {TEKS}; border: none; padding: 6px 8px; }}

    QScrollArea, QScrollArea > QWidget > QWidget {{ background: transparent; border: none; }}
    QScrollBar:vertical {{ background: transparent; width: 12px; margin: 0; }}
    QScrollBar::handle:vertical {{ background: rgba(255,255,255,0.18); border-radius: 3px;
                                   min-height: 40px; margin: 3px; }}
    QScrollBar::handle:vertical:hover {{ background: rgba(255,255,255,0.32); }}
    QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {{
        height: 0; background: none; }}
    QScrollBar:horizontal {{ height: 0; }}

    QLabel[peran="judul-besar"] {{ font-size: 56px; font-weight: 800; }}
    QLabel[peran="salam"] {{ font-size: 32px; font-weight: 800; }}
    QLabel[peran="judul-bagian"] {{ font-size: 22px; font-weight: 800; }}
    QLabel[peran="judul-panel"] {{ font-size: 16px; font-weight: 700; }}
    QLabel[peran="judul-lagu"] {{ font-size: 24px; font-weight: 800; }}
    QLabel[peran="judul"] {{ font-size: 15px; font-weight: 600; }}
    QLabel[peran="judul-kecil"] {{ font-size: 14px; font-weight: 600; }}
    QLabel[peran="kecil"] {{ font-size: 13px; color: {TEKS_REDUP}; }}
    QLabel[peran="label"] {{ font-size: 12px; font-weight: 700; color: {TEKS_REDUP}; }}
    QLabel[peran="info"] {{ font-size: 14px; color: #E5E5E5; }}
    QLabel[aktif="true"] {{ color: {AKSEN}; }}
    QLabel[peran="lirik"] {{ font-size: 28px; font-weight: 800; }}
    QLabel[peran="lirik"][keadaan="lewat"] {{ color: rgba(255,255,255,0.6); }}
    QLabel[peran="lirik"][keadaan="nanti"] {{ color: rgba(0,0,0,0.55); }}
    QLabel[peran="lirik"][keadaan="lewat"]:hover, QLabel[peran="lirik"][keadaan="nanti"]:hover {{
        color: {TEKS}; }}

    QPushButton {{ border: none; background: transparent; padding: 0; }}
    QPushButton[jenis="ikon"] {{ border-radius: 6px; }}
    QPushButton[jenis="ikon"]:hover {{ background: {TERPILIH}; }}
    QPushButton[jenis="ikon"]:disabled {{ background: transparent; }}
    QPushButton[jenis="garis"] {{ border: 1px solid #727272; border-radius: 16px; padding: 0 16px;
                                  min-height: 30px; font-size: 13px; font-weight: 700; }}
    QPushButton[jenis="garis"]:hover {{ border-color: {TEKS}; }}
    QPushButton[jenis="teks"] {{ color: {TEKS_REDUP}; font-size: 13px; font-weight: 700; }}
    QPushButton[jenis="teks"]:hover {{ color: {TEKS}; text-decoration: underline; }}
    QPushButton[jenis="rumah"] {{ background: {HOVER}; border-radius: 24px; }}
    QPushButton[jenis="rumah"]:hover {{ background: {TERPILIH}; }}

    QLineEdit#kotakCari {{ background: {HOVER}; border: 1px solid transparent; border-radius: 24px;
                           min-height: 46px; padding: 0 20px 0 8px; font-size: 15px; }}
    QLineEdit#kotakCari:hover {{ background: {TERPILIH}; border-color: #333333; }}
    QLineEdit#kotakCari:focus {{ background: {TERPILIH}; border-color: {TEKS}; }}

    #baris, #barisAntrean {{ border-radius: 6px; }}
    #baris:hover, #barisAntrean:hover {{ background: {HOVER}; }}
    #kartu {{ border-radius: 8px; }}
    #kartu:hover {{ background: {HOVER}; }}
    #ubin {{ background: rgba(255,255,255,0.08); border-radius: 6px; }}
    #ubin:hover {{ background: rgba(255,255,255,0.16); }}
    #kartuTeratas {{ background: #181818; border-radius: 8px; }}
    #kartuTeratas:hover {{ background: #242424; }}
    #kotakAbu {{ background: {HOVER}; border-radius: 8px; }}
    #itemKoleksi {{ border-radius: 6px; }}
    #itemKoleksi:hover {{ background: {HOVER}; }}
    #itemKoleksi[terpilih="true"] {{ background: {TERPILIH}; }}
    #kepalaTabel {{ border-bottom: 1px solid rgba(255,255,255,0.1); }}

    QMenu {{ background: {MENU}; padding: 4px; border: 1px solid #333333; }}
    QMenu::item {{ padding: 10px 24px 10px 12px; border-radius: 3px; color: #EDEDED; }}
    QMenu::item:selected {{ background: #3A3A3A; color: {TEKS}; }}
    QMenu::icon {{ padding-left: 8px; }}

    QSlider::groove:horizontal {{ height: 4px; background: #4D4D4D; border-radius: 2px; }}
    QSlider::sub-page:horizontal {{ background: {TEKS}; border-radius: 2px; }}
    QSlider::sub-page:horizontal:hover {{ background: {AKSEN}; }}
    QSlider::handle:horizontal {{ background: {TEKS}; width: 12px; height: 12px; margin: -4px 0;
                                  border-radius: 6px; }}

    QDialog, QMessageBox, QInputDialog {{ background: {MENU}; }}
    QDialog QLineEdit {{ background: {TERPILIH}; border: 1px solid #444; border-radius: 4px;
                         padding: 6px 8px; }}
    QDialog QPushButton {{ background: {TEKS}; color: {TEKS_DI_AKSEN}; border-radius: 14px;
                           padding: 6px 18px; font-weight: 700; min-width: 60px; }}

    #toast {{ background: {TEKS}; color: {TEKS_DI_AKSEN}; border-radius: 8px; padding: 10px 18px;
              font-size: 14px; font-weight: 600; }}
    """