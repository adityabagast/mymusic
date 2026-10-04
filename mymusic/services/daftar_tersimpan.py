"""Daftar lagu sederhana yang disimpan ke file JSON: Lagu yang Disukai dan riwayat "Baru diputar"."""
import json

from mymusic.models import Lagu


class DaftarTersimpan:
    """Isi file: [lagu, lagu, ...] dengan yang terbaru di depan. Satu lagu hanya muncul sekali."""

    def __init__(self, path, batas=None):
        self.path = path
        self.batas = batas  # None = tanpa batas
        self._lagu = self._baca()

    def _baca(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                return [Lagu.dari_dict(d) for d in json.load(f)]
        except FileNotFoundError:
            return []  # wajar saat aplikasi pertama kali dibuka

    def _tulis(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([lagu.ke_dict() for lagu in self._lagu], f, ensure_ascii=False, indent=2)

    def __len__(self):
        return len(self._lagu)

    def semua(self):
        return list(self._lagu)

    def ada(self, video_id):
        return any(lagu.video_id == video_id for lagu in self._lagu)

    def tambah(self, lagu):
        """Menaruh lagu di paling depan (bila sudah ada, dipindahkan ke depan, tidak dobel)."""
        self._lagu = [lagu] + [lama for lama in self._lagu if lama.video_id != lagu.video_id]
        if self.batas:
            self._lagu = self._lagu[:self.batas]
        self._tulis()

    def hapus(self, video_id):
        sisa = [lagu for lagu in self._lagu if lagu.video_id != video_id]
        if len(sisa) != len(self._lagu):
            self._lagu = sisa
            self._tulis()
