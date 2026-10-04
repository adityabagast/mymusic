"""Menyimpan playlist buatan pengguna ke file JSON."""
import json

from mymusic.config import FILE_PLAYLIST
from mymusic.models import Lagu


class PenyimpananPlaylist:
    """Isi file: {"Nama Playlist": [lagu, lagu, ...]}."""

    def __init__(self, path=FILE_PLAYLIST):
        self.path = path
        self._data = self._baca()

    def _baca(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                mentah = json.load(f)
        except FileNotFoundError:
            return {}  # wajar saat aplikasi pertama kali dibuka
        return {nama: [Lagu.dari_dict(d) for d in daftar] for nama, daftar in mentah.items()}

    def _tulis(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        mentah = {nama: [lagu.ke_dict() for lagu in daftar] for nama, daftar in self._data.items()}
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(mentah, f, ensure_ascii=False, indent=2)

    def semua_nama(self):
        return sorted(self._data)

    def ambil(self, nama):
        return list(self._data.get(nama, []))

    def simpan(self, nama, daftar_lagu):
        self._data[nama] = list(daftar_lagu)
        self._tulis()

    def hapus(self, nama):
        if self._data.pop(nama, None) is not None:
            self._tulis()