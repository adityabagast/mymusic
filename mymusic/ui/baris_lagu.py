"""Baris lagu ala tabel Spotify (# / judul / album / durasi / ⋯) dan daftar yang berisi baris-baris itu."""
from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMenu, QSizePolicy, QStackedLayout, QVBoxLayout, QWidget

from mymusic.config import AKSEN
from mymusic.ui.ikon import ikon, pixmap_ikon
from mymusic.ui.tema import TEKS, TEKS_REDUP
from mymusic.ui.widgets import LabelPotong, Sampul, TombolIkon, atur_properti, label

LEBAR_NOMOR, LEBAR_DURASI, LEBAR_TITIK, JARAK = 40, 56, 32, 16


def tampilkan_menu_lagu(induk, posisi, tambah, sisipkan):
    """Menu ⋯ / klik kanan sebuah lagu. `tambah` dan `sisipkan` adalah fungsi yang dipanggil."""
    menu = QMenu(induk)
    aksi_tambah = menu.addAction(ikon("tambah_antrean", TEKS_REDUP, 18), "Tambah ke antrean")
    aksi_sisipkan = menu.addAction(ikon("berikut", TEKS_REDUP, 18), "Putar berikutnya")
    dipilih = menu.exec(posisi)
    if dipilih is aksi_tambah:
        tambah()
    elif dipilih is aksi_sisipkan:
        sisipkan()


class BarisLagu(QFrame):
    putar = Signal()
    tambah = Signal()
    sisipkan = Signal()

    def __init__(self, nomor, lagu, tampil_album=True, ringkas=False):
        super().__init__()
        self.lagu = lagu
        self._ringkas = ringkas  # tanpa kolom nomor; tombol ▶ muncul di atas sampul
        self._aktif = False
        self._disorot = False
        self.setObjectName("baris")
        self.setAttribute(Qt.WA_StyledBackground)
        self.setAttribute(Qt.WA_Hover)
        self.setFixedHeight(56)

        self.tombol_putar = TombolIkon("putar", f"Putar {lagu.judul}", 16, 32)
        self.tombol_putar.ganti_ikon("putar", TEKS)
        self.tombol_putar.clicked.connect(lambda: self.putar.emit())
        sampul = Sampul(40)
        sampul.atur(lagu.sampul)
        if ringkas:
            self.tombol_putar.setParent(sampul)
            self.tombol_putar.setStyleSheet("background: rgba(0,0,0,0.55); border-radius: 4px;")
            self.tombol_putar.setGeometry(4, 4, 32, 32)
        else:
            # Kolom nomor: nomor biasa / tombol ▶ saat disorot / ikon speaker saat diputar.
            self.label_nomor = label(str(nomor), "kecil")
            self.label_nomor.setAlignment(Qt.AlignCenter)
            self.ikon_aktif = QLabel()
            self.ikon_aktif.setPixmap(pixmap_ikon("speaker", AKSEN, 16))
            self.ikon_aktif.setAlignment(Qt.AlignCenter)
            kolom_nomor = QWidget()
            kolom_nomor.setFixedWidth(LEBAR_NOMOR)
            self._tumpuk = QStackedLayout(kolom_nomor)
            for widget in (self.label_nomor, self.tombol_putar, self.ikon_aktif):
                self._tumpuk.addWidget(widget)

        self.label_judul = LabelPotong(lagu.judul, "judul")
        self.label_judul.setToolTip(lagu.teks)  # judul lengkap saat teksnya terpotong
        teks = QVBoxLayout()
        teks.setSpacing(2)
        teks.addStretch()
        teks.addWidget(self.label_judul)
        teks.addWidget(LabelPotong(lagu.artis or "—", "kecil"))
        teks.addStretch()
        blok_judul = QWidget()
        blok_judul.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        tata_judul = QHBoxLayout(blok_judul)
        tata_judul.setContentsMargins(0, 0, 0, 0)
        tata_judul.setSpacing(12)
        tata_judul.addWidget(sampul)
        tata_judul.addLayout(teks, 1)

        durasi = label(lagu.durasi, "kecil")
        durasi.setFixedWidth(LEBAR_DURASI)
        durasi.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.tombol_titik = TombolIkon("titik", f"Opsi lain untuk {lagu.judul}", 18, LEBAR_TITIK)
        kebijakan = self.tombol_titik.sizePolicy()
        kebijakan.setRetainSizeWhenHidden(True)  # tetap memakan tempat saat disembunyikan
        self.tombol_titik.setSizePolicy(kebijakan)
        self.tombol_titik.clicked.connect(
            lambda: self._tampilkan_menu(self.tombol_titik.mapToGlobal(QPoint(0, self.tombol_titik.height()))))

        tata = QHBoxLayout(self)
        tata.setContentsMargins(8 if ringkas else 16, 0, 8 if ringkas else 16, 0)
        tata.setSpacing(12 if ringkas else JARAK)
        if not ringkas:
            tata.addWidget(kolom_nomor)
        tata.addWidget(blok_judul, 4)
        if tampil_album:
            tata.addWidget(LabelPotong(lagu.album, "kecil"), 3)
        tata.addWidget(durasi)
        tata.addWidget(self.tombol_titik)
        self._segarkan()

    def atur_aktif(self, aktif):
        if aktif != self._aktif:
            self._aktif = aktif
            atur_properti(self.label_judul, "aktif", aktif)
            self._segarkan()

    def _segarkan(self):
        if self._ringkas:
            self.tombol_putar.setVisible(self._disorot)
        elif self._aktif:
            self._tumpuk.setCurrentWidget(self.ikon_aktif)
        elif self._disorot:
            self._tumpuk.setCurrentWidget(self.tombol_putar)
        else:
            self._tumpuk.setCurrentWidget(self.label_nomor)
        self.tombol_titik.setVisible(self._disorot)

    def _tampilkan_menu(self, posisi):
        tampilkan_menu_lagu(self, posisi, self.tambah.emit, self.sisipkan.emit)

    def enterEvent(self, event):
        self._disorot = True
        self._segarkan()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._disorot = False
        self._segarkan()
        super().leaveEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.putar.emit()

    def contextMenuEvent(self, event):
        self._tampilkan_menu(event.globalPos())


class KepalaTabel(QFrame):
    """Baris judul kolom: # | Judul | Album | jam. Lebarnya sama persis dengan BarisLagu."""

    def __init__(self, tampil_album=True):
        super().__init__()
        self.setObjectName("kepalaTabel")
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedHeight(36)
        tata = QHBoxLayout(self)
        tata.setContentsMargins(16, 0, 16, 0)
        tata.setSpacing(JARAK)
        pagar = label("#", "label")
        pagar.setFixedWidth(LEBAR_NOMOR)
        pagar.setAlignment(Qt.AlignCenter)
        tata.addWidget(pagar)
        tata.addWidget(LabelPotong("Judul", "label"), 4)
        if tampil_album:
            tata.addWidget(LabelPotong("Album", "label"), 3)
        jam = QLabel()
        jam.setPixmap(pixmap_ikon("jam", TEKS_REDUP, 16))
        jam.setFixedWidth(LEBAR_DURASI)
        jam.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        tata.addWidget(jam)
        tata.addSpacing(LEBAR_TITIK)


class DaftarLagu(QWidget):
    putar = Signal(int)  # posisi dalam daftar ini
    tambah = Signal(object)  # Lagu
    sisipkan = Signal(object)  # Lagu

    def __init__(self, tampil_album=True, kepala=False, ringkas=False):
        super().__init__()
        self._tampil_album = tampil_album
        self._ringkas = ringkas
        self._baris = []
        self._tata = QVBoxLayout(self)
        self._tata.setContentsMargins(0, 0, 0, 0)
        self._tata.setSpacing(0)
        if kepala:
            self._tata.addWidget(KepalaTabel(tampil_album))
            self._tata.addSpacing(8)

    def isi(self, daftar_lagu, nomor_awal=1, lagu_aktif=None):
        for baris in self._baris:
            self._tata.removeWidget(baris)
            baris.deleteLater()
        self._baris = []
        for i, lagu in enumerate(daftar_lagu):
            baris = BarisLagu(nomor_awal + i, lagu, self._tampil_album, self._ringkas)
            baris.putar.connect(lambda i=i: self.putar.emit(i))
            baris.tambah.connect(lambda lagu=lagu: self.tambah.emit(lagu))
            baris.sisipkan.connect(lambda lagu=lagu: self.sisipkan.emit(lagu))
            self._tata.addWidget(baris)
            self._baris.append(baris)
        self.tandai(lagu_aktif)

    def tandai(self, lagu_aktif):
        """Menandai baris lagu yang sedang diputar (kuning + ikon speaker)."""
        for baris in self._baris:
            baris.atur_aktif(lagu_aktif is not None and baris.lagu.video_id == lagu_aktif.video_id)
