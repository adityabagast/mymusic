"""Permintaan pindah halaman dari mana saja (nama artis/album yang diklik, kartu) ke JendelaUtama."""
from PySide6.QtCore import QObject, Signal


class Navigasi(QObject):
    buka_artis = Signal(str)  # id artis
    putar_artis = Signal(str)
    buka_album = Signal(str)  # id album
    putar_album = Signal(str)


_navigasi = None


def navigasi():
    """Satu Navigasi untuk seluruh aplikasi, seperti favorit(): widget yang letaknya jauh di dalam
    (mis. nama artis di sebuah baris lagu) tidak perlu meneruskan sinyal lewat banyak lapisan."""
    global _navigasi
    if _navigasi is None:
        _navigasi = Navigasi()
    return _navigasi
