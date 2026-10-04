"""Panel kanan: "Sedang diputar" (sampul besar + lagu berikutnya) atau "Antrean"."""
from PySide6.QtCore import QMimeData, Qt, Signal
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QPushButton, QScrollArea, QStackedLayout, QVBoxLayout, QWidget,
)

from mymusic.config import AKSEN, LEBAR_PANEL_KANAN
from mymusic.ui.widgets import LabelPotong, Sampul, TombolIkon, atur_properti, kosongkan_tata, label

DIPUTAR, ANTREAN = "diputar", "antrean"
MIME_POSISI = "application/x-mymusic-posisi"  # jenis data yang dibawa saat baris antrean diseret


class BarisAntrean(QFrame):
    putar = Signal()
    hapus = Signal()

    def __init__(self, lagu, bisa_dihapus=True, aktif=False, posisi=None):
        super().__init__()
        self.posisi = posisi  # posisi di antrean; None = baris tidak bisa diseret
        self._titik_tekan = None
        self.setObjectName("barisAntrean")
        self.setAttribute(Qt.WA_StyledBackground)
        self.setAttribute(Qt.WA_Hover)
        sampul = Sampul(48)
        sampul.atur(lagu.sampul)
        judul = LabelPotong(lagu.judul, "judul-kecil")
        atur_properti(judul, "aktif", aktif)
        teks = QVBoxLayout()
        teks.setSpacing(2)
        teks.addWidget(judul)
        teks.addWidget(LabelPotong(lagu.artis, "kecil"))
        tata = QHBoxLayout(self)
        tata.setContentsMargins(8, 8, 8, 8)
        tata.setSpacing(12)
        tata.addWidget(sampul)
        tata.addLayout(teks, 1)
        self.tombol_hapus = None
        if bisa_dihapus:
            self.tombol_hapus = TombolIkon("tutup", f"Hapus {lagu.judul} dari antrean", 16, 32)
            kebijakan = self.tombol_hapus.sizePolicy()
            kebijakan.setRetainSizeWhenHidden(True)
            self.tombol_hapus.setSizePolicy(kebijakan)
            self.tombol_hapus.hide()
            self.tombol_hapus.clicked.connect(lambda: self.hapus.emit())
            tata.addWidget(self.tombol_hapus)

    def enterEvent(self, event):
        if self.tombol_hapus:
            self.tombol_hapus.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.tombol_hapus:
            self.tombol_hapus.hide()
        super().leaveEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.putar.emit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._titik_tekan = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Seret dimulai setelah mouse bergerak cukup jauh sambil ditekan, agar klik biasa tidak ikut terseret.
        if (self.posisi is None or self._titik_tekan is None or not event.buttons() & Qt.LeftButton
                or (event.position().toPoint() - self._titik_tekan).manhattanLength()
                < QApplication.startDragDistance()):
            super().mouseMoveEvent(event)
            return
        self._titik_tekan = None
        data = QMimeData()
        data.setData(MIME_POSISI, str(self.posisi).encode())
        seret = QDrag(self)
        seret.setMimeData(data)
        seret.setPixmap(self.grab())
        seret.setHotSpot(event.position().toPoint())
        seret.exec(Qt.MoveAction)


class DaftarGeser(QWidget):
    """Wadah baris antrean yang urutannya bisa diubah dengan drag & drop."""
    dipindahkan = Signal(int, int)  # dari, ke (posisi di antrean)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.tata = QVBoxLayout(self)
        self.tata.setContentsMargins(0, 0, 0, 0)
        self.tata.setSpacing(0)
        self._garis = QFrame(self)  # penanda tempat lagu akan diletakkan
        self._garis.setStyleSheet(f"background: {AKSEN}; border-radius: 1px;")
        self._garis.hide()

    def _baris(self):
        semua = (self.tata.itemAt(i).widget() for i in range(self.tata.count()))
        return [baris for baris in semua if isinstance(baris, BarisAntrean)]

    def _tujuan(self, y):
        """Mengembalikan (posisi antrean tujuan, koordinat y garis penanda) untuk titik y."""
        baris = self._baris()
        for satu in baris:
            if y < satu.geometry().center().y():
                return satu.posisi, satu.geometry().top()
        return baris[-1].posisi + 1, baris[-1].geometry().bottom()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(MIME_POSISI) and self._baris():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        _, y = self._tujuan(event.position().toPoint().y())
        self._garis.setGeometry(8, max(y - 1, 0), self.width() - 16, 2)
        self._garis.show()
        self._garis.raise_()
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self._garis.hide()

    def dropEvent(self, event):
        self._garis.hide()
        ke, _ = self._tujuan(event.position().toPoint().y())
        dari = int(bytes(event.mimeData().data(MIME_POSISI)).decode())
        event.acceptProposedAction()
        self.dipindahkan.emit(dari, ke)


def _halaman_gulir(isi):
    gulir = QScrollArea()
    gulir.setWidgetResizable(True)
    gulir.setWidget(isi)
    return gulir


class PanelKanan(QFrame):
    tutup = Signal()
    simpan_antrean = Signal()

    def __init__(self, pemutar):
        super().__init__()
        self.pemutar = pemutar
        self.setObjectName("panel")
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedWidth(LEBAR_PANEL_KANAN)
        self._tumpuk = QStackedLayout(self)
        self.halaman_diputar = self._buat_diputar()
        self.halaman_antrean = self._buat_antrean()
        self._tumpuk.addWidget(self.halaman_diputar)
        self._tumpuk.addWidget(self.halaman_antrean)
        pemutar.lagu_berubah.connect(self._segarkan)
        pemutar.antrean_berubah.connect(self._segarkan)

    # ---------- tampilan ----------

    def _kepala(self, label_judul):
        tombol = TombolIkon("tutup", "Tutup panel", 18, 32)
        tombol.clicked.connect(lambda: self.tutup.emit())
        tata = QHBoxLayout()
        tata.setContentsMargins(16, 16, 12, 12)
        tata.addWidget(label_judul, 1)
        tata.addWidget(tombol)
        return tata

    def _buat_diputar(self):
        self.label_sumber = LabelPotong("", "judul-panel")
        self.sampul_besar = Sampul(LEBAR_PANEL_KANAN - 32, sudut=8)
        self.label_judul = label("", "judul-lagu")
        self.label_judul.setWordWrap(True)
        self.label_artis = label("", "kecil")
        self.label_artis.setStyleSheet("font-size: 15px;")

        tombol_buka = QPushButton("Buka antrean")
        tombol_buka.setProperty("jenis", "teks")
        tombol_buka.setCursor(Qt.PointingHandCursor)
        tombol_buka.clicked.connect(lambda: self.tampilkan(ANTREAN))
        judul_kotak = label("Berikutnya dalam antrean", "judul-kecil")
        judul_kotak.setStyleSheet("font-weight: 700;")
        kepala_kotak = QHBoxLayout()
        kepala_kotak.addWidget(judul_kotak, 1)
        kepala_kotak.addWidget(tombol_buka)
        self._tata_berikut = QVBoxLayout()
        kotak = QFrame()
        kotak.setObjectName("kotakAbu")
        kotak.setAttribute(Qt.WA_StyledBackground)
        tata_kotak = QVBoxLayout(kotak)
        tata_kotak.setContentsMargins(16, 12, 16, 12)
        tata_kotak.addLayout(kepala_kotak)
        tata_kotak.addLayout(self._tata_berikut)

        isi = QWidget()
        tata_isi = QVBoxLayout(isi)
        tata_isi.setContentsMargins(16, 0, 16, 16)
        tata_isi.setSpacing(4)
        tata_isi.addWidget(self.sampul_besar)
        tata_isi.addSpacing(12)
        tata_isi.addWidget(self.label_judul)
        tata_isi.addWidget(self.label_artis)
        tata_isi.addSpacing(20)
        tata_isi.addWidget(kotak)
        tata_isi.addStretch()

        halaman = QWidget()
        tata = QVBoxLayout(halaman)
        tata.setContentsMargins(0, 0, 0, 0)
        tata.addLayout(self._kepala(self.label_sumber))
        tata.addWidget(_halaman_gulir(isi), 1)
        return halaman

    def _buat_antrean(self):
        self.label_berikut_dari = LabelPotong("", "judul-kecil")
        self.label_berikut_dari.setStyleSheet("font-weight: 700;")
        tombol_kosongkan = QPushButton("Kosongkan")
        tombol_kosongkan.setProperty("jenis", "teks")
        tombol_kosongkan.setCursor(Qt.PointingHandCursor)
        tombol_kosongkan.clicked.connect(self.pemutar.kosongkan)
        baris_berikut = QHBoxLayout()
        baris_berikut.setContentsMargins(8, 16, 8, 4)
        baris_berikut.addWidget(self.label_berikut_dari, 1)
        baris_berikut.addWidget(tombol_kosongkan)

        judul_sekarang = label("Sedang diputar", "judul-kecil")
        judul_sekarang.setStyleSheet("font-weight: 700;")
        judul_sekarang.setContentsMargins(8, 4, 8, 4)
        self._tata_sekarang = QVBoxLayout()
        self.daftar_geser = DaftarGeser()
        self.daftar_geser.dipindahkan.connect(self.pemutar.pindahkan)

        isi = QWidget()
        tata_isi = QVBoxLayout(isi)
        tata_isi.setContentsMargins(8, 0, 8, 8)
        tata_isi.setSpacing(0)
        tata_isi.addWidget(judul_sekarang)
        tata_isi.addLayout(self._tata_sekarang)
        tata_isi.addLayout(baris_berikut)
        tata_isi.addWidget(self.daftar_geser)
        tata_isi.addStretch()

        tombol_simpan = QPushButton("Simpan antrean sebagai playlist")
        tombol_simpan.setProperty("jenis", "garis")
        tombol_simpan.setCursor(Qt.PointingHandCursor)
        tombol_simpan.setMinimumHeight(40)
        tombol_simpan.clicked.connect(lambda: self.simpan_antrean.emit())
        bawah = QHBoxLayout()
        bawah.setContentsMargins(16, 12, 16, 16)
        bawah.addWidget(tombol_simpan)

        halaman = QWidget()
        tata = QVBoxLayout(halaman)
        tata.setContentsMargins(0, 0, 0, 0)
        tata.addLayout(self._kepala(label("Antrean", "judul-panel")))
        tata.addWidget(_halaman_gulir(isi), 1)
        tata.addLayout(bawah)
        return halaman

    # ---------- isi ----------

    def tampilkan(self, mode):
        self._tumpuk.setCurrentWidget(self.halaman_diputar if mode == DIPUTAR else self.halaman_antrean)
        self.show()
        self._segarkan()

    def mode(self):
        if self.isHidden():
            return None
        return DIPUTAR if self._tumpuk.currentWidget() is self.halaman_diputar else ANTREAN

    def _segarkan(self, *_):
        if self.isHidden():
            return  # tidak perlu menggambar ulang panel yang tidak terlihat
        antrean = self.pemutar.antrean
        lagu = antrean.sekarang
        sumber = self.pemutar.sumber or "Antrean"
        if self.mode() == DIPUTAR:
            self.label_sumber.setText(sumber if lagu else "Sedang diputar")
            self.sampul_besar.atur(lagu.sampul if lagu else "")
            self.label_judul.setText(lagu.judul if lagu else "Belum ada lagu diputar")
            self.label_artis.setText(lagu.artis if lagu else "")
            kosongkan_tata(self._tata_berikut)
            posisi = antrean.indeks + 1
            if lagu and posisi < len(antrean):
                baris = BarisAntrean(antrean.lagu[posisi], bisa_dihapus=False)
                baris.putar.connect(lambda: self.pemutar.putar_di(posisi))
                self._tata_berikut.addWidget(baris)
            else:
                kosong = label("Tidak ada lagu berikutnya. Tambahkan lewat menu ⋯ di setiap lagu.", "kecil")
                kosong.setWordWrap(True)
                self._tata_berikut.addWidget(kosong)
            return

        kosongkan_tata(self._tata_sekarang)
        kosongkan_tata(self.daftar_geser.tata)
        if lagu:
            self._tata_sekarang.addWidget(BarisAntrean(lagu, bisa_dihapus=False, aktif=True))
        self.label_berikut_dari.setText(f"Berikutnya dari: {sumber}")
        for posisi in range(antrean.indeks + 1, len(antrean)):
            baris = BarisAntrean(antrean.lagu[posisi], posisi=posisi)
            baris.setToolTip("Seret untuk mengubah urutan · klik dua kali untuk memutar")
            baris.putar.connect(lambda posisi=posisi: self.pemutar.putar_di(posisi))
            baris.hapus.connect(lambda posisi=posisi: self.pemutar.hapus([posisi]))
            self.daftar_geser.tata.addWidget(baris)
        if antrean.indeks + 1 >= len(antrean):
            kosong = label("Antrean kosong. Tambahkan lagu lewat menu ⋯ atau klik kanan.", "kecil")
            kosong.setWordWrap(True)
            kosong.setContentsMargins(8, 24, 8, 24)
            self.daftar_geser.tata.addWidget(kosong)
