"""Titik masuk aplikasi. Jalankan dengan:  python main.py"""
import sys

from PySide6.QtWidgets import QApplication

from mymusic.ui.jendela_utama import JendelaUtama
from mymusic.ui.tema import muat_font, stylesheet


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(stylesheet(muat_font()))
    jendela = JendelaUtama()
    jendela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()