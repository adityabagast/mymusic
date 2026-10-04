"""Panel kiri "Koleksi Kamu": daftar playlist yang tersimpan."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from mymusic.config import AKSEN, LEBAR_KOLEKSI
from mymusic.ui.ikon import pixmap_ikon
from mymusic.ui.tema import TEKS
from mymusic.ui.widgets import LabelPotong, Sampul, TombolIkon, atur_properti, kosongkan_tata, label


class ItemKoleksi(QFrame):
    klik = Signal()
    putar = Signal()

    def __init__(self, nama, keterangan, url_sampul):
        super().__init__()
        self.nama = nama
        self.setObjectName("itemKoleksi")
        self.setAttribute(Qt.WA_StyledBackground)
        self.setAttribute(Qt.WA_Hover)
        self.setCursor(Qt.PointingHandCursor)
        sampul = Sampul(48)
        sampul.atur(url_sampul)
        self.label_nama = LabelPotong(nama, "judul")
        self.ikon_diputar = QLabel()
        self.ikon_diputar.setPixmap(pixmap_ikon("speaker", AKSEN, 16))
        self.ikon_diputar.hide()
        teks = QVBoxLayout()
        teks.setSpacing(2)
        teks.addWidget(self.label_nama)
        teks.addWidget(LabelPotong(keterangan, "kecil"))
        tata = QHBoxLayout(self)
        tata.setContentsMargins(8, 8, 12, 8)
        tata.setSpacing(12)
        tata.addWidget(sampul)
        tata.addLayout(teks, 1)
        tata.addWidget(self.ikon_diputar)

    def atur_status(self, terpilih, diputar):
        atur_properti(self, "terpilih", terpilih)
        atur_properti(self.label_nama, "aktif", diputar)
        self.ikon_diputar.setVisible(diputar)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.rect().contains(event.position().toPoint()):
            self.klik.emit()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.putar.emit()


class PanelKoleksi(QFrame):
    buka = Signal(str)
    putar = Signal(str)
    simpan_antrean = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("panel")
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedWidth(LEBAR_KOLEKSI)
        self._item = []

        ikon_koleksi = QLabel()
        ikon_koleksi.setPixmap(pixmap_ikon("koleksi", TEKS, 22))
        tombol_tambah = TombolIkon("tambah", "Simpan antrean sebagai playlist baru", 18, 32)
        tombol_tambah.clicked.connect(lambda: self.simpan_antrean.emit())
        kepala = QHBoxLayout()
        kepala.setContentsMargins(20, 16, 12, 8)
        kepala.setSpacing(10)
        kepala.addWidget(ikon_koleksi)
        kepala.addWidget(label("Koleksi Kamu", "judul-panel"), 1)
        kepala.addWidget(tombol_tambah)

        isi = QWidget()
        self._tata_item = QVBoxLayout(isi)
        self._tata_item.setContentsMargins(8, 0, 8, 8)
        self._tata_item.setSpacing(0)
        self._tata_item.addStretch()
        gulir = QScrollArea()
        gulir.setWidgetResizable(True)
        gulir.setWidget(isi)

        self.label_kosong = label("Belum ada playlist. Simpan antreanmu dengan tombol +, "
                                  "atau simpan playlist YouTube yang kamu buka.", "kecil")
        self.label_kosong.setWordWrap(True)
        self.label_kosong.setContentsMargins(20, 8, 20, 8)

        tata = QVBoxLayout(self)
        tata.setContentsMargins(0, 0, 0, 0)
        tata.setSpacing(0)
        tata.addLayout(kepala)
        tata.addWidget(self.label_kosong)
        tata.addWidget(gulir, 1)

    def isi(self, daftar):
        """daftar = [(nama, keterangan, url_sampul), ...]"""
        kosongkan_tata(self._tata_item)
        self._item = []
        for nama, keterangan, sampul in daftar:
            item = ItemKoleksi(nama, keterangan, sampul)
            item.klik.connect(lambda nama=nama: self.buka.emit(nama))
            item.putar.connect(lambda nama=nama: self.putar.emit(nama))
            self._tata_item.addWidget(item)
            self._item.append(item)
        self._tata_item.addStretch()
        self.label_kosong.setVisible(not daftar)

    def tandai(self, terpilih=None, diputar=None):
        for item in self._item:
            item.atur_status(item.nama == terpilih, item.nama == diputar)
