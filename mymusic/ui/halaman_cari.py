"""Halaman hasil pencarian: Hasil teratas + 4 lagu, lalu Lagu lainnya."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

from mymusic.ui.baris_lagu import DaftarLagu
from mymusic.ui.kartu import KartuTeratas
from mymusic.ui.widgets import label

JUMLAH_ATAS = 4


class HalamanCari(QScrollArea):
    putar = Signal(int)  # posisi di daftar hasil
    tambah = Signal(object)
    sisipkan = Signal(object)

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        isi = QWidget()
        self.setWidget(isi)
        tata = QVBoxLayout(isi)
        tata.setContentsMargins(24, 24, 24, 32)
        tata.setSpacing(12)

        self.label_status = label("", "kecil")
        tata.addWidget(self.label_status)

        self._teratas = None
        self.wadah_hasil = QWidget()
        tata_hasil = QVBoxLayout(self.wadah_hasil)
        tata_hasil.setContentsMargins(0, 0, 0, 0)
        tata_hasil.setSpacing(12)

        self.kartu_teratas = KartuTeratas()
        self.daftar_atas = DaftarLagu(tampil_album=False, ringkas=True)
        kiri = QVBoxLayout()
        kiri.setSpacing(12)
        kiri.addWidget(label("Hasil teratas", "judul-bagian"))
        kiri.addWidget(self.kartu_teratas)
        kiri.addStretch()
        kanan = QVBoxLayout()
        kanan.setSpacing(12)
        kanan.addWidget(label("Lagu", "judul-bagian"))
        kanan.addWidget(self.daftar_atas)
        kanan.addStretch()
        baris_atas = QHBoxLayout()
        baris_atas.setSpacing(24)
        baris_atas.addLayout(kiri, 2)
        baris_atas.addLayout(kanan, 3)
        tata_hasil.addLayout(baris_atas)

        self.label_lainnya = label("Lagu lainnya", "judul-bagian")
        self.daftar_lainnya = DaftarLagu(tampil_album=True)
        tata_hasil.addSpacing(20)
        tata_hasil.addWidget(self.label_lainnya)
        tata_hasil.addWidget(self.daftar_lainnya)
        tata.addWidget(self.wadah_hasil)
        tata.addStretch()

        self.kartu_teratas.putar.connect(lambda: self.putar.emit(0))
        self.daftar_atas.putar.connect(self.putar.emit)
        self.daftar_lainnya.putar.connect(lambda i: self.putar.emit(i + JUMLAH_ATAS))
        for daftar in (self.daftar_atas, self.daftar_lainnya):
            daftar.tambah.connect(self.tambah.emit)
            daftar.sisipkan.connect(self.sisipkan.emit)
        self.tampilkan_pesan("Ketik judul lagu atau nama artis di kotak cari.")

    def tampilkan_pesan(self, teks):
        self.label_status.setText(teks)
        self.label_status.show()
        self.wadah_hasil.hide()

    def tampilkan_memuat(self, kata):
        self.tampilkan_pesan(f"Mencari “{kata}”…")

    def tampilkan(self, kata, daftar_lagu, lagu_aktif=None):
        if not daftar_lagu:
            self.tampilkan_pesan(f"Tidak ada hasil untuk “{kata}”.")
            return
        self.label_status.hide()
        self.wadah_hasil.show()
        self.kartu_teratas.atur(daftar_lagu[0])
        self.daftar_atas.isi(daftar_lagu[:JUMLAH_ATAS], 1)
        self.daftar_lainnya.isi(daftar_lagu[JUMLAH_ATAS:], JUMLAH_ATAS + 1)
        self.label_lainnya.setVisible(len(daftar_lagu) > JUMLAH_ATAS)
        self._teratas = daftar_lagu[0]
        self.tandai(lagu_aktif)
        self.verticalScrollBar().setValue(0)

    def tandai(self, lagu_aktif):
        if self.wadah_hasil.isHidden():
            return
        self.kartu_teratas.atur_aktif(lagu_aktif is not None and lagu_aktif.video_id == self._teratas.video_id)
        self.daftar_atas.tandai(lagu_aktif)
        self.daftar_lainnya.tandai(lagu_aktif)
