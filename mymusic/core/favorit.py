"""Lagu yang Disukai: satu sumber data untuk semua tombol ♥ di aplikasi."""
from PySide6.QtCore import QObject, Signal

from mymusic.config import FILE_FAVORIT
from mymusic.services.daftar_tersimpan import DaftarTersimpan


class Favorit(QObject):
    berubah = Signal(object, bool)  # Lagu, apakah sekarang disukai

    def __init__(self, path=FILE_FAVORIT, parent=None):
        super().__init__(parent)
        self._daftar = DaftarTersimpan(path)

    def __len__(self):
        return len(self._daftar)

    def semua(self):
        return self._daftar.semua()

    def ada(self, lagu):
        return lagu is not None and self._daftar.ada(lagu.video_id)

    def alihkan(self, lagu):
        """Suka ↔ batal suka. Mengembalikan True bila lagu sekarang disukai."""
        disukai = not self.ada(lagu)
        if disukai:
            self._daftar.tambah(lagu)
        else:
            self._daftar.hapus(lagu.video_id)
        self.berubah.emit(lagu, disukai)
        return disukai


_favorit = None


def favorit():
    """Satu Favorit untuk seluruh aplikasi (dibuat saat pertama dipakai), seperti pemuat_sampul()."""
    global _favorit
    if _favorit is None:
        _favorit = Favorit()
    return _favorit
