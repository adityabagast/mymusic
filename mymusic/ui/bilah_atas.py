"""Bilah paling atas: logo, tombol ← →, tombol Beranda, dan kotak cari."""
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QWidget

from mymusic.config import FILE_IKON, LEBAR_KOLEKSI, NAMA_APLIKASI
from mymusic.ui.ikon import ikon
from mymusic.ui.tema import TEKS, TEKS_REDUP
from mymusic.ui.widgets import TombolIkon, label


class BilahAtas(QWidget):
    cari = Signal(str)
    beranda = Signal()
    mundur = Signal()
    maju = Signal()

    def __init__(self):
        super().__init__()
        self.setFixedHeight(64)

        logo = QLabel()
        logo.setFixedSize(32, 32)
        logo.setPixmap(QIcon(str(FILE_IKON)).pixmap(32, 32))  # sama dengan ikon di taskbar
        nama = label(NAMA_APLIKASI)
        nama.setStyleSheet("font-size: 18px; font-weight: 800;")
        kiri = QWidget()
        kiri.setFixedWidth(LEBAR_KOLEKSI)
        tata_kiri = QHBoxLayout(kiri)
        tata_kiri.setContentsMargins(16, 0, 0, 0)
        tata_kiri.setSpacing(10)
        tata_kiri.addWidget(logo)
        tata_kiri.addWidget(nama)
        tata_kiri.addStretch()
        self.tombol_mundur = TombolIkon("kembali", "Kembali (Alt+←)", 22, 36)
        self.tombol_maju = TombolIkon("maju", "Maju (Alt+→)", 22, 36)
        self.tombol_mundur.clicked.connect(lambda: self.mundur.emit())
        self.tombol_maju.clicked.connect(lambda: self.maju.emit())
        tata_kiri.addWidget(self.tombol_mundur)
        tata_kiri.addWidget(self.tombol_maju)
        self.atur_navigasi(False, False)

        self.tombol_rumah = QPushButton()
        self.tombol_rumah.setProperty("jenis", "rumah")
        self.tombol_rumah.setFixedSize(48, 48)
        self.tombol_rumah.setIconSize(QSize(24, 24))
        self.tombol_rumah.setCursor(Qt.PointingHandCursor)
        self.tombol_rumah.setToolTip("Beranda")
        self.tombol_rumah.clicked.connect(lambda: self.beranda.emit())
        self.atur_beranda_aktif(True)

        self.kotak_cari = QLineEdit()
        self.kotak_cari.setObjectName("kotakCari")
        self.kotak_cari.setPlaceholderText("Mau dengar apa? Atau tempel link playlist YouTube")
        self.kotak_cari.setMaximumWidth(480)
        self.kotak_cari.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.kotak_cari.addAction(ikon("cari", TEKS_REDUP, 22), QLineEdit.LeadingPosition)
        self.kotak_cari.returnPressed.connect(self._kirim)

        tata = QHBoxLayout(self)
        tata.setContentsMargins(0, 0, 0, 0)
        tata.setSpacing(8)
        tata.addWidget(kiri)
        tata.addStretch(1)
        tata.addWidget(self.tombol_rumah)
        tata.addWidget(self.kotak_cari, 3)
        tata.addStretch(1)
        tata.addSpacing(LEBAR_KOLEKSI)  # penyeimbang agar kotak cari tetap di tengah

    def _kirim(self):
        teks = self.kotak_cari.text().strip()
        if teks:
            self.cari.emit(teks)

    def atur_navigasi(self, bisa_mundur, bisa_maju):
        for tombol, nama_ikon, bisa in ((self.tombol_mundur, "kembali", bisa_mundur),
                                        (self.tombol_maju, "maju", bisa_maju)):
            tombol.setEnabled(bisa)
            tombol.ganti_ikon(nama_ikon, TEKS if bisa else "#535353")

    def atur_beranda_aktif(self, aktif):
        self.tombol_rumah.setIcon(ikon("rumah", TEKS if aktif else TEKS_REDUP, 24))

    def fokus_cari(self):
        self.kotak_cari.setFocus()
        self.kotak_cari.selectAll()
