"""Bilah paling atas: logo, tombol Beranda, dan kotak cari."""
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QWidget

from mymusic.config import AKSEN, LEBAR_KOLEKSI, NAMA_APLIKASI
from mymusic.ui.ikon import ikon, pixmap_ikon
from mymusic.ui.tema import TEKS, TEKS_DI_AKSEN, TEKS_REDUP
from mymusic.ui.widgets import label


class BilahAtas(QWidget):
    cari = Signal(str)
    beranda = Signal()

    def __init__(self):
        super().__init__()
        self.setFixedHeight(64)

        logo = QLabel()
        logo.setFixedSize(32, 32)
        logo.setAlignment(Qt.AlignCenter)
        logo.setPixmap(pixmap_ikon("not", TEKS_DI_AKSEN, 18, tebal=2.4))
        logo.setStyleSheet(f"background: {AKSEN}; border-radius: 8px;")
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

    def atur_beranda_aktif(self, aktif):
        self.tombol_rumah.setIcon(ikon("rumah", TEKS if aktif else TEKS_REDUP, 24))

    def fokus_cari(self):
        self.kotak_cari.setFocus()
        self.kotak_cari.selectAll()
