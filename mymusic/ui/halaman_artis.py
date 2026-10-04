"""Halaman artis: banner besar ala Spotify, tombol putar, lagu populer, album, single, dan artis serupa."""
from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

from mymusic.config import AKSEN
from mymusic.core.sampul import pemuat_sampul
from mymusic.ui.baris_lagu import DaftarLagu
from mymusic.ui.kartu import BagianKartu, kartu_album, kartu_artis
from mymusic.ui.tema import TEKS_REDUP, TERPILIH
from mymusic.ui.widgets import LabelPotong, LatarGradasi, TombolBulat, TombolIkon, label, warna_dominan

TINGGI_KEPALA = 340
JUMLAH_POPULER = 5


class KepalaArtis(QWidget):
    """Banner foto artis (dipotong agar memenuhi lebar) dengan nama besar di kiri bawah."""
    warna_siap = Signal(object)  # QColor dominan banner, untuk latar halaman di bawahnya

    def __init__(self):
        super().__init__()
        self.setFixedHeight(TINGGI_KEPALA)
        self._gambar = None
        self._url = ""
        self.label_jenis = label("Artis", "judul-kecil")
        self.label_nama = LabelPotong("", "judul-besar")
        self.label_info = label("", "info")
        tata = QVBoxLayout(self)
        tata.setContentsMargins(24, 24, 24, 24)
        tata.setSpacing(8)
        tata.addStretch()
        tata.addWidget(self.label_jenis)
        tata.addWidget(self.label_nama)
        tata.addWidget(self.label_info)

    def atur(self, nama, info, url_gambar):
        self.label_nama.setText(nama)
        self.label_nama.setToolTip(nama)
        ukuran = 72 if len(nama) <= 14 else 56 if len(nama) <= 22 else 40
        self.label_nama.setStyleSheet(f"font-size: {ukuran}px;")
        self.label_info.setText(info)
        if url_gambar != self._url:
            self._url = url_gambar
            self._gambar = None
            self.update()
            pemuat_sampul().muat(url_gambar, lambda gambar, url=url_gambar: self._terima(url, gambar))

    def _terima(self, url, gambar):
        if url == self._url:
            self._gambar = gambar
            self.update()
            self.warna_siap.emit(warna_dominan(gambar))

    def paintEvent(self, event):
        pelukis = QPainter(self)
        pelukis.setRenderHint(QPainter.SmoothPixmapTransform)
        if self._gambar is None:
            pelukis.fillRect(self.rect(), QColor(TERPILIH))
        else:
            # Seperti object-fit: cover — skala agar memenuhi, lalu ambil bagian tengah-atas (wajah).
            sumber = self._gambar.size()
            skala = max(self.width() / sumber.width(), self.height() / sumber.height())
            lebar, tinggi = self.width() / skala, self.height() / skala
            pelukis.drawPixmap(QRectF(self.rect()), self._gambar,
                               QRectF((sumber.width() - lebar) / 2, (sumber.height() - tinggi) * 0.3, lebar, tinggi))
        # Bayangan di bawah agar nama yang putih tetap terbaca di atas foto yang terang.
        bayangan = QLinearGradient(0, self.height() * 0.35, 0, self.height())
        bayangan.setColorAt(0, QColor(0, 0, 0, 0))
        bayangan.setColorAt(1, QColor(0, 0, 0, 170))
        pelukis.fillRect(self.rect(), bayangan)


class HalamanArtis(QScrollArea):
    putar = Signal(int)  # posisi di lagu populer
    putar_jeda = Signal()
    acak = Signal()
    tambah = Signal(object)
    sisipkan = Signal(object)

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.artis = None  # Artis yang sedang ditampilkan

        self.latar = LatarGradasi(TINGGI_KEPALA + 320)
        self.setWidget(self.latar)
        tata = QVBoxLayout(self.latar)
        tata.setContentsMargins(0, 0, 0, 32)
        tata.setSpacing(0)

        self.kepala = KepalaArtis()
        self.kepala.warna_siap.connect(self.latar.atur_warna)
        tata.addWidget(self.kepala)

        self.tombol_putar = TombolBulat(56, keterangan="Putar")
        self.tombol_acak = TombolIkon("acak", "Acak", 28, 44)
        aksi = QHBoxLayout()
        aksi.setContentsMargins(24, 24, 24, 8)
        aksi.setSpacing(20)
        aksi.addWidget(self.tombol_putar)
        aksi.addWidget(self.tombol_acak)
        aksi.addStretch()
        tata.addLayout(aksi)

        isi = QVBoxLayout()
        isi.setContentsMargins(24, 0, 24, 0)
        isi.setSpacing(0)
        self.label_status = label("", "kecil")
        self.label_populer = label("Populer", "judul-bagian")
        self.daftar = DaftarLagu(tampil_album=True)
        self.bagian_album = BagianKartu("Album")
        self.bagian_single = BagianKartu("Single & EP")
        self.bagian_serupa = BagianKartu("Penggemar juga menyukai")
        isi.addWidget(self.label_status)
        isi.addSpacing(12)
        isi.addWidget(self.label_populer)
        isi.addSpacing(12)
        isi.addWidget(self.daftar)
        for bagian in (self.bagian_album, self.bagian_single, self.bagian_serupa):
            isi.addWidget(bagian)
        tata.addLayout(isi)
        tata.addStretch()

        self.tombol_putar.clicked.connect(lambda: self.putar_jeda.emit())
        self.tombol_acak.clicked.connect(lambda: self.acak.emit())
        self.daftar.putar.connect(self.putar.emit)
        self.daftar.tambah.connect(self.tambah.emit)
        self.daftar.sisipkan.connect(self.sisipkan.emit)

    def tampilkan_memuat(self):
        self.artis = None
        self.kepala.atur("", "", "")
        self.latar.atur_warna(TERPILIH)
        self._isi_bagian(())
        self.label_status.setText("Memuat artis…")
        self.label_status.show()
        self.verticalScrollBar().setValue(0)

    def tampilkan_gagal(self, pesan):
        self.label_status.setText(pesan)
        self.label_status.show()

    def tampilkan(self, artis, lagu_aktif=None):
        self.artis = artis
        info = f"{artis.pendengar} pendengar bulanan" if artis.pendengar else ""
        self.kepala.atur(artis.nama, info, artis.gambar)
        self.label_status.hide()
        self._isi_bagian(artis.lagu[:JUMLAH_POPULER], artis)
        self.tandai(lagu_aktif)
        self.verticalScrollBar().setValue(0)

    def _isi_bagian(self, lagu, artis=None):
        self.label_populer.setVisible(bool(lagu))
        self.daftar.isi(list(lagu))
        self.bagian_album.isi([kartu_album(info) for info in artis.album] if artis else [])
        self.bagian_single.isi([kartu_album(info) for info in artis.single] if artis else [])
        self.bagian_serupa.isi([kartu_artis(info) for info in artis.serupa] if artis else [])

    def tandai(self, lagu_aktif):
        self.daftar.tandai(lagu_aktif)

    def atur_main(self, sedang_main):
        self.tombol_putar.atur_main(sedang_main)

    def atur_acak(self, aktif):
        self.tombol_acak.ganti_ikon("acak", AKSEN if aktif else TEKS_REDUP)
        self.tombol_acak.setToolTip("Acak: aktif" if aktif else "Acak: mati")
