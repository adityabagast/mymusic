"""Komponen kecil yang dipakai ulang di banyak tempat."""
from PySide6.QtCore import QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPalette, QRegion
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QSizePolicy, QWidget

from mymusic.config import AKSEN
from mymusic.core.sampul import pemuat_sampul
from mymusic.services.youtube import perbesar_sampul
from mymusic.ui.ikon import ikon, pixmap_ikon
from mymusic.ui.tema import PANEL, TEKS_DI_AKSEN, TEKS_REDUP, TERPILIH


def atur_properti(widget, nama, nilai):
    """Mengubah properti yang dipakai QSS (mis. aktif="true") lalu menerapkan ulang gayanya."""
    widget.setProperty(nama, nilai)
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def label(teks="", peran=None):
    hasil = QLabel(teks)
    if peran:
        hasil.setProperty("peran", peran)
    return hasil


class LabelPotong(QLabel):
    """QLabel yang memotong teks panjang dengan '…' alih-alih melebarkan tata letak."""

    def __init__(self, teks="", peran=None):
        super().__init__(teks)
        if peran:
            self.setProperty("peran", peran)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)

    def minimumSizeHint(self):
        return QSize(0, super().minimumSizeHint().height())

    def paintEvent(self, event):
        pelukis = QPainter(self)
        teks = self.fontMetrics().elidedText(self.text(), Qt.ElideRight, self.width())
        self.style().drawItemText(pelukis, self.rect(), int(self.alignment()), self.palette(),
                                  self.isEnabled(), teks, QPalette.WindowText)


class TombolIkon(QPushButton):
    def __init__(self, nama_ikon, keterangan, ukuran_ikon=20, ukuran=36):
        super().__init__()
        self.setProperty("jenis", "ikon")
        self.setFixedSize(ukuran, ukuran)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(keterangan)
        self.setAccessibleName(keterangan)
        self._ukuran_ikon = ukuran_ikon
        self.ganti_ikon(nama_ikon)

    def ganti_ikon(self, nama_ikon, warna=TEKS_REDUP):
        self.setIcon(ikon(nama_ikon, warna, self._ukuran_ikon))
        self.setIconSize(QSize(self._ukuran_ikon, self._ukuran_ikon))


class TombolBulat(QPushButton):
    """Tombol putar/jeda bulat (aksen di header & kartu, putih di bilah pemutar)."""

    def __init__(self, ukuran=56, warna=AKSEN, keterangan="Putar"):
        super().__init__()
        self.setFixedSize(ukuran, ukuran)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(keterangan)
        self.setAccessibleName(keterangan)
        self.setStyleSheet(f"QPushButton {{ background: {warna}; border-radius: {ukuran // 2}px; }}"
                           f"QPushButton:hover {{ background: {QColor(warna).lighter(112).name()}; }}")
        self._ukuran_ikon = int(ukuran * 0.4)
        self.atur_main(False)

    def atur_main(self, sedang_main):
        self.setIcon(ikon("jeda" if sedang_main else "putar", TEKS_DI_AKSEN, self._ukuran_ikon))
        self.setIconSize(QSize(self._ukuran_ikon, self._ukuran_ikon))


def warna_dominan(gambar):
    """Rata-rata warna sebuah gambar, digelapkan sedikit agar cocok untuk latar gradasi."""
    rata = gambar.toImage().scaled(1, 1, Qt.IgnoreAspectRatio, Qt.SmoothTransformation).pixelColor(0, 0)
    h, s, v, _ = rata.getHsvF()
    return QColor.fromHsvF(max(h, 0), min(s * 1.1, 1), min(max(v, 0.25), 0.55))


class Sampul(QWidget):
    """Gambar sampul persegi bersudut bulat. Selama gambar belum ada, tampil kotak dengan ikon not."""
    gambar_siap = Signal(object)  # QPixmap

    def __init__(self, ukuran, sudut=4):
        super().__init__()
        self.setFixedSize(ukuran, ukuran)
        self._sudut = sudut
        self._gambar = None
        self._url = ""

    def atur(self, url):
        url = perbesar_sampul(url, 544 if self.width() > 120 else 120)
        if url == self._url:
            return
        self._url = url
        self._gambar = None
        self.update()
        pemuat_sampul().muat(url, lambda gambar, url=url: self._terima(url, gambar))

    def _terima(self, url, gambar):
        if url != self._url:
            return  # sudah diganti gambar lain
        self._gambar = gambar
        self.update()
        self.gambar_siap.emit(gambar)

    def paintEvent(self, event):
        pelukis = QPainter(self)
        pelukis.setRenderHint(QPainter.Antialiasing)
        pelukis.setRenderHint(QPainter.SmoothPixmapTransform)
        jalur = QPainterPath()
        jalur.addRoundedRect(QRectF(self.rect()), self._sudut, self._sudut)
        pelukis.setClipPath(jalur)
        if self._gambar is None:
            pelukis.fillRect(self.rect(), QColor(TERPILIH))
            sisi = max(self.width() // 3, 12)
            pelukis.drawPixmap((self.width() - sisi) // 2, (self.height() - sisi) // 2,
                               pixmap_ikon("not", "#6A6A6A", sisi))
            return
        # Isi penuh kotak (potong bagian lebih), seperti object-fit: cover.
        sumber = self._gambar.size()
        sisi = min(sumber.width(), sumber.height())
        pelukis.drawPixmap(self.rect(), self._gambar,
                           QRectF((sumber.width() - sisi) / 2, (sumber.height() - sisi) / 2, sisi, sisi).toRect())


class LatarGradasi(QWidget):
    """Latar halaman yang bergradasi dari sebuah warna ke warna panel, seperti header playlist Spotify."""

    def __init__(self, tinggi_gradasi=360):
        super().__init__()
        self._warna = QColor(PANEL)
        self._tinggi = tinggi_gradasi

    def atur_warna(self, warna):
        self._warna = QColor(warna)
        self.update()

    def paintEvent(self, event):
        pelukis = QPainter(self)
        gradasi = QLinearGradient(0, 0, 0, self._tinggi)
        gradasi.setColorAt(0, self._warna)
        gradasi.setColorAt(1, QColor(PANEL))
        pelukis.fillRect(self.rect(), QColor(PANEL))
        pelukis.fillRect(0, 0, self.width(), self._tinggi, gradasi)


class Toast(QLabel):
    """Pesan singkat di bawah tengah jendela yang hilang sendiri."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("toast")
        self.hide()
        self._timer = QTimer(self, singleShot=True, interval=2200)
        self._timer.timeout.connect(self.hide)

    def tampilkan(self, teks, jarak_bawah=100):
        self.setText(teks)
        self.adjustSize()
        induk = self.parentWidget()
        self.move((induk.width() - self.width()) // 2, induk.height() - self.height() - jarak_bawah)
        self.raise_()
        self.show()
        self._timer.start()


class PanelBulat(QFrame):
    """Panel bersudut bulat yang juga memotong isinya, agar latar gradasi tidak keluar dari sudut."""

    def __init__(self):
        super().__init__()
        self.setObjectName("panel")
        self.setAttribute(Qt.WA_StyledBackground)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        jalur = QPainterPath()
        jalur.addRoundedRect(QRectF(self.rect()), 8, 8)
        self.setMask(QRegion(jalur.toFillPolygon().toPolygon()))


def campur_warna(warna_a, warna_b, porsi_a):
    """Mencampur dua warna, mis. 22% aksen + 78% warna panel."""
    a, b = QColor(warna_a), QColor(warna_b)
    return QColor(*(round(x * porsi_a + y * (1 - porsi_a)) for x, y in
                    ((a.red(), b.red()), (a.green(), b.green()), (a.blue(), b.blue()))))


def kosongkan_tata(tata):
    """Menghapus semua widget di dalam sebuah layout."""
    while tata.count():
        item = tata.takeAt(0)
        if item.widget():
            item.widget().hide()  # langsung hilang dari layar; objeknya dihapus Qt sesaat kemudian
            item.widget().deleteLater()