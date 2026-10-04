"""Kartu, ubin, dan rak untuk halaman Beranda & Cari."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget

from mymusic.config import AKSEN
from mymusic.ui.widgets import LabelPotong, Sampul, TombolBulat, atur_properti, label


class _BisaDiklik(QFrame):
    """QFrame yang memancarkan `klik` saat diklik kiri dan memunculkan tombol putar saat disorot."""
    klik = Signal()
    putar = Signal()

    def _siapkan(self, nama_objek, tombol_putar):
        self.setObjectName(nama_objek)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setAttribute(Qt.WA_Hover)
        self.setCursor(Qt.PointingHandCursor)
        self.tombol_putar = tombol_putar
        self.tombol_putar.clicked.connect(lambda: self.putar.emit())
        self.tombol_putar.hide()

    def enterEvent(self, event):
        self.tombol_putar.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.tombol_putar.hide()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.rect().contains(event.position().toPoint()):
            self.klik.emit()


class Kartu(_BisaDiklik):
    LEBAR = 168

    def __init__(self, judul, keterangan, url_sampul):
        super().__init__()
        self.setFixedWidth(self.LEBAR)
        sampul = Sampul(self.LEBAR - 24, sudut=6)
        sampul.atur(url_sampul)
        self._siapkan("kartu", TombolBulat(44, AKSEN, f"Putar {judul}"))
        self.tombol_putar.setParent(sampul)  # melayang di pojok kanan bawah sampul
        self.tombol_putar.move(sampul.width() - 52, sampul.height() - 52)

        tata = QVBoxLayout(self)
        tata.setContentsMargins(12, 12, 12, 12)
        tata.setSpacing(6)
        tata.addWidget(sampul)
        tata.addSpacing(2)
        tata.addWidget(LabelPotong(judul, "judul"))
        tata.addWidget(LabelPotong(keterangan, "kecil"))


class Ubin(_BisaDiklik):
    """Pintasan playlist di bagian atas Beranda."""

    def __init__(self, judul, url_sampul):
        super().__init__()
        self.setFixedHeight(64)
        sampul = Sampul(64, sudut=6)
        sampul.atur(url_sampul)
        self._siapkan("ubin", TombolBulat(40, AKSEN, f"Putar {judul}"))
        kebijakan = self.tombol_putar.sizePolicy()
        kebijakan.setRetainSizeWhenHidden(True)  # tetap memakan tempat agar teks tidak bergeser
        self.tombol_putar.setSizePolicy(kebijakan)
        nama = LabelPotong(judul, "judul")
        nama.setStyleSheet("font-weight: 700;")
        tata = QHBoxLayout(self)
        tata.setContentsMargins(0, 0, 12, 0)
        tata.setSpacing(16)
        tata.addWidget(sampul)
        tata.addWidget(nama, 1)
        tata.addWidget(self.tombol_putar)


class RakKartu(QWidget):
    """Satu baris kartu. Kartu yang tidak muat di lebar saat ini disembunyikan."""

    def __init__(self):
        super().__init__()
        self._kartu = []
        self._tata = QHBoxLayout(self)
        self._tata.setContentsMargins(0, 0, 0, 0)
        self._tata.setSpacing(0)
        self._tata.addStretch()

    def isi(self, daftar_kartu):
        for kartu in self._kartu:
            kartu.deleteLater()
        self._kartu = list(daftar_kartu)
        for i, kartu in enumerate(self._kartu):
            self._tata.insertWidget(i, kartu)
        self._atur_yang_tampil()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._atur_yang_tampil()

    def _atur_yang_tampil(self):
        muat = max(1, self.width() // Kartu.LEBAR)
        for i, kartu in enumerate(self._kartu):
            kartu.setVisible(i < muat)


class KartuTeratas(_BisaDiklik):
    """Kartu besar "Hasil teratas" di halaman Cari."""

    def __init__(self):
        super().__init__()
        self.setFixedHeight(232)
        self.sampul = Sampul(92, sudut=6)
        self._siapkan("kartuTeratas", TombolBulat(48, AKSEN, "Putar hasil teratas"))
        self.tombol_putar.setParent(self)
        self.label_judul = LabelPotong("", "salam")
        self.label_keterangan = label("", "kecil")
        tata = QVBoxLayout(self)
        tata.setContentsMargins(20, 20, 20, 20)
        tata.setSpacing(12)
        tata.addWidget(self.sampul)
        tata.addStretch()
        tata.addWidget(self.label_judul)
        tata.addWidget(self.label_keterangan)

    def atur(self, lagu):
        self.sampul.atur(lagu.sampul)
        self.label_judul.setText(lagu.judul)
        self.label_keterangan.setText(f"Lagu · {lagu.artis}")

    def atur_aktif(self, aktif):
        atur_properti(self.label_judul, "aktif", aktif)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.tombol_putar.move(self.width() - 68, self.height() - 68)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.putar.emit()
