"""Menyimpan keadaan aplikasi saat ditutup (volume, antrean, mode putar, panel) ke file JSON."""
import json

from mymusic.config import FILE_SESI


class PenyimpananSesi:
    def __init__(self, path=FILE_SESI):
        self.path = path

    def baca(self):
        """Isi sesi terakhir, atau {} bila belum ada / rusak (sesi yang hilang tidak berbahaya)."""
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
        return data if isinstance(data, dict) else {}

    def simpan(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
