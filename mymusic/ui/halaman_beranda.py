"""Halaman Beranda: salam, pintasan playlist, baru diputar, rekomendasi lagu & playlist, ajakan impor link."""
from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from mymusic.config import AKSEN, BATAS_REKOMENDASI
from mymusic.ui.ikon import pixmap_ikon
from mymusic.ui.kartu import Kartu, RakKartu, Ubin
from mymusic.ui.tema import PANEL, TEKS, TERPILIH
from mymusic.ui.widgets import LatarGradasi, campur_warna, kosongkan_tata, label


def salam_waktu():
    jam = datetime.now().hour
    if jam < 11:
        return "Selamat pagi"
    if jam < 15:
        return "Selamat siang"
    if jam < 18:
        return "Selamat sore"
    return "Selamat malam"


class BagianLagu(QWidget):
    """Satu rak kartu lagu (judul + keterangan + kartu). Tersembunyi selama belum ada isinya."""
    putar = Signal(object, int, str)  # daftar lagu, posisi, nama sumber antrean

    def __init__(self, keterangan):
        super().__init__()
        self.label_judul = label("", "judul-bagian")
        self.rak = RakKartu()
        tata = QVBoxLayout(self)
        tata.setContentsMargins(0, 36, 0, 0)
        tata.setSpacing(2)
        tata.addWidget(self.label_judul)
        tata.addWidget(label(keterangan, "kecil"))
        tata.addSpacing(6)
        tata.addWidget(self.rak)
        self.hide()

    def isi(self, judul, daftar_lagu, sumber):
        self.label_judul.setText(judul)
        kartu = []
        for i, lagu in enumerate(daftar_lagu):
            satu = Kartu(lagu.judul, lagu.artis, lagu.sampul)
            satu.klik.connect(lambda i=i: self.putar.emit(daftar_lagu, i, sumber))
            satu.putar.connect(lambda i=i: self.putar.emit(daftar_lagu, i, sumber))
            kartu.append(satu)
        self.rak.isi(kartu)
        self.setVisible(bool(daftar_lagu))


class HalamanBeranda(QScrollArea):
    buka_playlist_saya = Signal(str)
    putar_playlist_saya = Signal(str)
    buka_playlist_yt = Signal(object)  # InfoPlaylist
    putar_playlist_yt = Signal(object)  # InfoPlaylist
    putar_lagu = Signal(object, int, str)  # daftar lagu, posisi, nama sumber antrean
    minta_tempel_link = Signal()

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)

        latar = LatarGradasi(320)
        latar.atur_warna(campur_warna(AKSEN, PANEL, 0.22))
        self.setWidget(latar)
        tata = QVBoxLayout(latar)
        tata.setContentsMargins(24, 24, 24, 32)
        tata.setSpacing(0)

        self.label_salam = label(salam_waktu(), "salam")
        tata.addWidget(self.label_salam)
        tata.addSpacing(20)

        self.wadah_ubin = QWidget()
        self.grid_ubin = QGridLayout(self.wadah_ubin)
        self.grid_ubin.setContentsMargins(0, 0, 0, 0)
        self.grid_ubin.setSpacing(8)
        tata.addWidget(self.wadah_ubin)

        self.bagian_riwayat = BagianLagu("Lagu yang terakhir kamu putar")
        self.bagian_rekomendasi = BagianLagu("Lagu serupa, diperbarui setiap kali lagu berganti")
        self.bagian_suka = BagianLagu("Lagu serupa dengan salah satu lagu favoritmu")
        for bagian in (self.bagian_riwayat, self.bagian_rekomendasi, self.bagian_suka):
            bagian.putar.connect(self.putar_lagu.emit)
            tata.addWidget(bagian)

        tata.addSpacing(32)
        tata.addWidget(label("Playlist rekomendasi", "judul-bagian"))
        tata.addSpacing(2)
        tata.addWidget(label("Dari YouTube Music — buka, putar, atau simpan ke Koleksi Kamu", "kecil"))
        tata.addSpacing(6)
        self.label_status_playlist = label("Memuat rekomendasi…", "kecil")
        self.rak_playlist = RakKartu()
        tata.addWidget(self.label_status_playlist)
        tata.addWidget(self.rak_playlist)

        tata.addSpacing(28)
        tata.addWidget(self._buat_ajakan())
        tata.addStretch()

    def _buat_ajakan(self):
        kotak = QFrame()
        kotak.setObjectName("kotakAbu")
        kotak.setAttribute(Qt.WA_StyledBackground)
        lingkaran = QLabel()
        lingkaran.setFixedSize(56, 56)
        lingkaran.setAlignment(Qt.AlignCenter)
        lingkaran.setPixmap(pixmap_ikon("link", TEKS, 24))
        lingkaran.setStyleSheet(f"background: {TERPILIH}; border-radius: 28px;")
        teks = QVBoxLayout()
        teks.setSpacing(4)
        judul = label("Punya playlist di YouTube?", "judul")
        keterangan = label("Tempel link-nya di kotak cari di atas — semua lagunya langsung muncul "
                           "dan bisa disimpan ke Koleksi Kamu.", "kecil")
        keterangan.setWordWrap(True)
        teks.addWidget(judul)
        teks.addWidget(keterangan)
        tombol = QPushButton("Tempel link")
        tombol.setProperty("jenis", "garis")
        tombol.setCursor(Qt.PointingHandCursor)
        tombol.clicked.connect(lambda: self.minta_tempel_link.emit())
        tata = QHBoxLayout(kotak)
        tata.setContentsMargins(20, 20, 20, 20)
        tata.setSpacing(20)
        tata.addWidget(lingkaran)
        tata.addLayout(teks, 1)
        tata.addWidget(tombol)
        return kotak

    def showEvent(self, event):
        self.label_salam.setText(salam_waktu())
        super().showEvent(event)

    def isi_pintasan(self, daftar):
        """daftar = [(nama_playlist, url_sampul), ...] dari Koleksi Kamu."""
        kosongkan_tata(self.grid_ubin)
        for i, (nama, sampul) in enumerate(daftar[:6]):
            ubin = Ubin(nama, sampul)
            ubin.klik.connect(lambda nama=nama: self.buka_playlist_saya.emit(nama))
            ubin.putar.connect(lambda nama=nama: self.putar_playlist_saya.emit(nama))
            self.grid_ubin.addWidget(ubin, i // 2, i % 2)
        self.wadah_ubin.setVisible(bool(daftar))

    def tampilkan_riwayat(self, daftar_lagu):
        self.bagian_riwayat.isi("Baru diputar", daftar_lagu[:BATAS_REKOMENDASI], "Baru diputar")

    def tampilkan_rekomendasi_lagu(self, lagu_asal, daftar_lagu):
        self.bagian_rekomendasi.isi(f"Karena kamu memutar “{lagu_asal.judul}”", daftar_lagu,
                                    f"Karena kamu memutar {lagu_asal.judul}")

    def tampilkan_mirip_suka(self, lagu_asal, daftar_lagu):
        self.bagian_suka.isi(f"Karena kamu menyukai “{lagu_asal.judul}”", daftar_lagu,
                             f"Karena kamu menyukai {lagu_asal.judul}")

    def tampilkan_playlist_rekomendasi(self, daftar_info):
        kartu = []
        for info in daftar_info:
            satu = Kartu(info.judul, info.keterangan or "Playlist · YouTube Music", info.sampul)
            satu.klik.connect(lambda info=info: self.buka_playlist_yt.emit(info))
            satu.putar.connect(lambda info=info: self.putar_playlist_yt.emit(info))
            kartu.append(satu)
        self.rak_playlist.isi(kartu)
        self.label_status_playlist.setVisible(not daftar_info)
        self.label_status_playlist.setText("Belum ada rekomendasi.")

    def tampilkan_gagal_playlist(self, pesan):
        self.label_status_playlist.setText(f"Rekomendasi gagal dimuat: {pesan}")
