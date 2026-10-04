"""Menjalankan fungsi lambat (jaringan) di thread lain agar jendela tidak macet."""
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal


class SinyalPekerja(QObject):
    selesai = Signal(object)
    gagal = Signal(str)


class Pekerja(QRunnable):
    def __init__(self, fungsi, *args):
        super().__init__()
        self.fungsi = fungsi
        self.args = args
        self.sinyal = SinyalPekerja()

    def run(self):
        try:
            sinyal, nilai = self.sinyal.selesai, self.fungsi(*self.args)
        except Exception as e:
            sinyal, nilai = self.sinyal.gagal, str(e)
        try:
            sinyal.emit(nilai)
        except RuntimeError:
            pass  # jendela sudah ditutup sebelum pekerjaan ini selesai


# Pekerja yang sedang berjalan disimpan di sini. Tanpa referensi ini, Python bisa
# membuang pekerja (beserta fungsi callback-nya) sebelum hasilnya sempat diterima.
_pekerja_aktif = set()


def jalankan_di_latar(fungsi, *args, selesai=None, gagal=None):
    """Jalankan fungsi(*args) di latar, lalu panggil selesai(hasil) atau gagal(pesan)."""
    pekerja = Pekerja(fungsi, *args)

    def beres(callback, nilai):
        _pekerja_aktif.discard(pekerja)
        if callback:
            callback(nilai)

    pekerja.sinyal.selesai.connect(lambda hasil: beres(selesai, hasil))
    pekerja.sinyal.gagal.connect(lambda pesan: beres(gagal, pesan))
    _pekerja_aktif.add(pekerja)
    QThreadPool.globalInstance().start(pekerja)