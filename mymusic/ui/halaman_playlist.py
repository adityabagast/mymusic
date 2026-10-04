"""Halaman playlist: header bergradasi dari warna sampul, tombol aksi, lalu tabel lagu."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QScrollArea, QVBoxLayout

from mymusic.config import AKSEN
from mymusic.ui.baris_lagu import DaftarLagu
from mymusic.ui.tema import TEKS_REDUP, TERPILIH
from mymusic.ui.widgets import (
    SAMPUL_SUKA, LabelPotong, LatarGradasi, Sampul, TombolBulat, TombolIkon, label, warna_dominan,
)

SAYA, YOUTUBE, SUKA = "saya", "youtube", "suka"  # SUKA = Lagu yang Disukai


class HalamanPlaylist(QScrollArea):
    putar = Signal(int)
    putar_jeda = Signal()
    tambah = Signal(object)
    sisipkan = Signal(object)
    tambah_semua = Signal()
    acak = Signal()
    simpan = Signal()
    hapus = Signal()

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.jenis = None
        self.judul = ""
        self.daftar_lagu = []

        self.latar = LatarGradasi(440)
        self.setWidget(self.latar)
        tata = QVBoxLayout(self.latar)
        tata.setContentsMargins(0, 0, 0, 32)
        tata.setSpacing(0)

        self.sampul = Sampul(200, sudut=6)
        self.sampul.gambar_siap.connect(lambda gambar: self.latar.atur_warna(warna_dominan(gambar)))
        self.label_jenis = label("", "judul-kecil")
        self.label_judul = LabelPotong("", "judul-besar")
        self.label_info = label("", "info")
        teks = QVBoxLayout()
        teks.setSpacing(8)
        teks.addStretch()
        teks.addWidget(self.label_jenis)
        teks.addWidget(self.label_judul)
        teks.addWidget(self.label_info)
        kepala = QHBoxLayout()
        kepala.setContentsMargins(24, 56, 24, 24)
        kepala.setSpacing(24)
        kepala.addWidget(self.sampul)
        kepala.addLayout(teks, 1)
        tata.addLayout(kepala)

        self.tombol_putar = TombolBulat(56, keterangan="Putar playlist")
        self.tombol_acak = TombolIkon("acak", "Acak", 28, 44)
        self.tombol_simpan = TombolIkon("simpan", "Simpan ke Koleksi Kamu", 30, 44)
        self.tombol_antrean = TombolIkon("tambah_antrean", "Tambah semua ke antrean", 28, 44)
        self.tombol_hapus = TombolIkon("hapus", "Hapus playlist", 26, 44)
        aksi = QHBoxLayout()
        aksi.setContentsMargins(24, 8, 24, 20)
        aksi.setSpacing(20)
        for tombol in (self.tombol_putar, self.tombol_acak, self.tombol_simpan, self.tombol_antrean, self.tombol_hapus):
            aksi.addWidget(tombol)
        aksi.addStretch()
        tata.addLayout(aksi)

        self.label_status = label("", "kecil")
        self.label_status.setContentsMargins(24, 0, 24, 0)
        self.daftar = DaftarLagu(tampil_album=True, kepala=True)
        bungkus = QVBoxLayout()
        bungkus.setContentsMargins(24, 0, 24, 0)
        bungkus.addWidget(self.daftar)
        tata.addWidget(self.label_status)
        tata.addLayout(bungkus)
        tata.addStretch()

        self.tombol_putar.clicked.connect(lambda: self.putar_jeda.emit())
        self.tombol_acak.clicked.connect(lambda: self.acak.emit())
        self.tombol_simpan.clicked.connect(lambda: self.simpan.emit())
        self.tombol_antrean.clicked.connect(lambda: self.tambah_semua.emit())
        self.tombol_hapus.clicked.connect(lambda: self.hapus.emit())
        self.daftar.putar.connect(self.putar.emit)
        self.daftar.tambah.connect(self.tambah.emit)
        self.daftar.sisipkan.connect(self.sisipkan.emit)

    def tampilkan_memuat(self, judul):
        self._isi_kepala(YOUTUBE, judul, "")
        self.label_info.setText("Memuat isi playlist…")
        self.label_status.hide()
        self.daftar.isi([])

    def tampilkan_gagal(self, pesan):
        self.label_info.setText("")
        self.label_status.setText(pesan)
        self.label_status.show()

    def tampilkan(self, jenis, judul, daftar_lagu, lagu_aktif=None):
        self.daftar_lagu = daftar_lagu
        sampul = SAMPUL_SUKA if jenis == SUKA else daftar_lagu[0].sampul if daftar_lagu else ""
        self._isi_kepala(jenis, judul, sampul)
        menit = round(sum(lagu.detik for lagu in daftar_lagu) / 60)
        pemilik = "YouTube" if jenis == YOUTUBE else "Kamu"
        self.label_info.setText(f"{pemilik} · {len(daftar_lagu)} lagu, sekitar {menit} menit")
        self.label_status.setVisible(not daftar_lagu)
        self.label_status.setText("Lagu yang kamu sukai akan muncul di sini. Klik ♥ pada lagu mana pun untuk menyimpannya."
                                  if jenis == SUKA else "Playlist ini kosong.")
        self.daftar.isi(daftar_lagu, 1, lagu_aktif)

    def _isi_kepala(self, jenis, judul, url_sampul):
        self.jenis = jenis
        self.judul = judul
        self.label_jenis.setText("Playlist YouTube" if jenis == YOUTUBE else "Playlist")
        self.label_judul.setText(judul)
        self.label_judul.setToolTip(judul)
        # Judul panjang dikecilkan hurufnya (seperti Spotify), baru dipotong bila masih kepanjangan.
        ukuran = 56 if len(judul) <= 16 else 40 if len(judul) <= 28 else 30
        self.label_judul.setStyleSheet(f"font-size: {ukuran}px;")
        self.latar.atur_warna(TERPILIH)  # sementara, sampai warna sampul diketahui
        self.sampul.atur(url_sampul)
        self.tombol_simpan.setVisible(jenis == YOUTUBE)
        self.tombol_hapus.setVisible(jenis == SAYA)
        self.verticalScrollBar().setValue(0)

    def atur_acak(self, aktif):
        self.tombol_acak.ganti_ikon("acak", AKSEN if aktif else TEKS_REDUP)
        self.tombol_acak.setToolTip("Acak: aktif" if aktif else "Acak: mati")

    def atur_main(self, sedang_main):
        self.tombol_putar.atur_main(sedang_main)

    def tandai(self, lagu_aktif):
        self.daftar.tandai(lagu_aktif)
