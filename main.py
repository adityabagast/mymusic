"""Titik masuk aplikasi. Jalankan dengan:  python main.py"""
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from mymusic.config import FILE_IKON, ID_APLIKASI
from mymusic.ui.jendela_utama import JendelaUtama
from mymusic.ui.tema import muat_font, stylesheet


def main():
    if sys.platform == "win32":
        # Tanpa ini Windows menganggap kita "python.exe" dan memakai ikon Python di taskbar.
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(ID_APLIKASI)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(FILE_IKON)))  # berlaku untuk semua jendela & dialog
    app.setStyleSheet(stylesheet(muat_font()))
    jendela = JendelaUtama()
    jendela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()