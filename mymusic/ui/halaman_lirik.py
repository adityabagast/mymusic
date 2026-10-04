"""Halaman lirik: latar dari warna sampul, baris yang sedang dinyanyikan disorot dan diikuti otomatis."""
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from mymusic.config import JEDA_IKUTI_LIRIK_MS
from mymusic.core.sampul import pemuat_sampul
from mymusic.services.youtube import perbesar_sampul
from mymusic.ui.tema import PANEL
from mymusic.ui.widgets import atur_properti, kosongkan_tata, label, warna_dominan


class BarisLirik(QLabel):
    klik = Signal()

    def __init__(self, teks, bisa_diklik):
        super().__init__(teks)
        self.setProperty("peran", "lirik")
        self.setWordWrap(True)
        self.setAttribute(Qt.WA_Hover)  # agar :hover di QSS berlaku pada QLabel
        if bisa_diklik:
            self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.klik.emit()


class HalamanLirik(QScrollArea):
    geser = Signal(int)  # milidetik: baris lirik diklik

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.video_id = None  # lagu yang liriknya sedang ditampilkan / dimuat
        self._lirik = None
        self._baris = []
        self._indeks = -1
        self._posisi = 0
        self._warna = QColor(PANEL)
        self._url_sampul = ""

        isi = QWidget()
        self.setWidget(isi)
        tata = QVBoxLayout(isi)
        tata.setContentsMargins(48, 40, 48, 48)
        tata.setSpacing(0)
        self.label_pesan = label("", "judul-bagian")
        self.label_pesan.setWordWrap(True)
        self.label_keterangan = label("", "info")
        self.label_keterangan.setWordWrap(True)
        self._tata_baris = QVBoxLayout()
        self._tata_baris.setSpacing(14)
        self.label_sumber = label("", "info")
        tata.addWidget(self.label_pesan)
        tata.addWidget(self.label_keterangan)
        tata.addSpacing(16)
        tata.addLayout(self._tata_baris)
        tata.addSpacing(32)
        tata.addWidget(self.label_sumber)
        tata.addStretch()

        self._animasi = QPropertyAnimation(self.verticalScrollBar(), b"value", self)
        self._animasi.setDuration(350)
        self._animasi.setEasingCurve(QEasingCurve.OutCubic)
        self._ikuti = True
        self._timer_ikuti = QTimer(self, singleShot=True, interval=JEDA_IKUTI_LIRIK_MS)
        self._timer_ikuti.timeout.connect(self._ikuti_lagi)

    # ---------- latar ----------

    def paintEvent(self, event):
        QPainter(self.viewport()).fillRect(self.viewport().rect(), self._warna)

    def _atur_latar(self, url_sampul):
        url = perbesar_sampul(url_sampul, 120)
        if url == self._url_sampul:
            return
        self._url_sampul = url
        self._warna = QColor(PANEL)
        self.viewport().update()
        pemuat_sampul().muat(url, lambda gambar, url=url: self._sampul_siap(url, gambar))

    def _sampul_siap(self, url, gambar):
        if url == self._url_sampul:
            self._warna = warna_dominan(gambar)
            self.viewport().update()

    # ---------- isi ----------

    def tampilkan_kosong(self):
        self.video_id = None
        self._atur_latar("")
        self._isi("Putar lagu untuk melihat liriknya.")

    def tampilkan_memuat(self, lagu):
        self.video_id = lagu.video_id
        self._atur_latar(lagu.sampul)
        self._isi("Memuat lirik…")

    def tampilkan_gagal(self, lagu, pesan):
        if lagu.video_id != self.video_id:
            return
        self.video_id = None  # agar dicoba lagi saat halaman dibuka berikutnya
        self._isi("Lirik gagal dimuat.", pesan)

    def tampilkan(self, lagu, lirik):
        """Menampilkan hasil ambil_lirik(); lirik None berarti lagu ini tidak punya lirik."""
        if lagu.video_id != self.video_id:
            return  # hasil untuk lagu sebelumnya datang terlambat
        if lirik is None or not lirik.baris:
            self._isi("Lirik untuk lagu ini belum tersedia.")
            return
        keterangan = "" if lirik.bersinkron else "Lirik ini belum tersinkron dengan lagu."
        self._isi("", keterangan, lirik)
        self.atur_posisi(self._posisi)

    def _isi(self, pesan, keterangan="", lirik=None):
        self._lirik = lirik
        self._baris = []
        self._indeks = -1
        self.label_pesan.setText(pesan)
        self.label_pesan.setVisible(bool(pesan))
        self.label_keterangan.setText(keterangan)
        self.label_keterangan.setVisible(bool(keterangan))
        kosongkan_tata(self._tata_baris)
        if lirik:
            for i, teks in enumerate(lirik.baris):
                baris = BarisLirik(teks, lirik.bersinkron)
                atur_properti(baris, "keadaan", "nanti" if lirik.bersinkron else "biasa")
                if lirik.bersinkron:
                    baris.klik.connect(lambda waktu=lirik.waktu[i]: self.geser.emit(waktu))
                self._tata_baris.addWidget(baris)
                self._baris.append(baris)
        sumber = lirik.sumber if lirik else ""
        self.label_sumber.setText(f"Lirik dari {sumber}" if sumber else "")
        self.label_sumber.setVisible(bool(sumber))
        self._animasi.stop()
        self.verticalScrollBar().setValue(0)

    # ---------- mengikuti lagu ----------

    def atur_posisi(self, milidetik):
        """Dipanggil terus selama lagu berjalan; menyorot baris yang sedang dinyanyikan."""
        self._posisi = milidetik
        if not self._lirik or not self._lirik.bersinkron:
            return
        indeks = self._lirik.indeks_pada(milidetik)
        if indeks == self._indeks:
            return
        self._indeks = indeks
        for i, baris in enumerate(self._baris):
            keadaan = "lewat" if i < indeks else "aktif" if i == indeks else "nanti"
            if baris.property("keadaan") != keadaan:
                atur_properti(baris, "keadaan", keadaan)
        if self._ikuti and indeks >= 0:
            self._gulir_ke(self._baris[indeks])

    def _gulir_ke(self, baris):
        """Menggulir halus agar baris aktif berada sedikit di atas tengah, seperti Spotify."""
        tujuan = baris.y() + baris.height() // 2 - int(self.viewport().height() * 0.4)
        tujuan = max(0, min(tujuan, self.verticalScrollBar().maximum()))
        self._animasi.stop()
        self._animasi.setStartValue(self.verticalScrollBar().value())
        self._animasi.setEndValue(tujuan)
        self._animasi.start()

    def wheelEvent(self, event):
        # Pengguna sedang membaca bagian lain: jangan ditarik kembali ke baris aktif dulu.
        self._animasi.stop()
        self._ikuti = False
        self._timer_ikuti.start()
        super().wheelEvent(event)

    def _ikuti_lagi(self):
        self._ikuti = True
        if 0 <= self._indeks < len(self._baris):
            self._gulir_ke(self._baris[self._indeks])
