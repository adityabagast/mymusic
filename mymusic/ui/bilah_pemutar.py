"""Bilah pemutar di bawah: lagu yang diputar | kendali + progres | panel & volume."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QSizePolicy, QSlider, QVBoxLayout, QWidget

from mymusic.config import AKSEN, VOLUME_AWAL
from mymusic.core.antrean import ULANG_MATI, ULANG_SATU
from mymusic.ui.ikon import pixmap_ikon
from mymusic.ui.tema import TEKS, TEKS_REDUP
from mymusic.ui.widgets import LabelPotong, Sampul, TombolBulat, TombolIkon, label


def format_waktu(ms):
    detik = ms // 1000
    return f"{detik // 60}:{detik % 60:02}"


class BilahPemutar(QWidget):
    panel_diminta = Signal(str)  # "diputar" atau "antrean"

    def __init__(self, pemutar, parent=None):
        super().__init__(parent)
        self.pemutar = pemutar
        self._sedang_geser = False
        self.setFixedHeight(80)
        self._buat_tampilan()
        self._sambungkan_sinyal()
        self._tampilkan_lagu(None)

    def _buat_tampilan(self):
        # Kiri: sampul + judul + artis
        self.sampul = Sampul(56)
        self.label_judul = LabelPotong("", "judul-kecil")
        self.label_artis = LabelPotong("", "kecil")
        self.label_artis.setStyleSheet("font-size: 12px;")
        teks = QVBoxLayout()
        teks.setSpacing(2)
        teks.addStretch()
        teks.addWidget(self.label_judul)
        teks.addWidget(self.label_artis)
        teks.addStretch()
        kiri = QWidget()
        tata_kiri = QHBoxLayout(kiri)
        tata_kiri.setContentsMargins(0, 0, 0, 0)
        tata_kiri.setSpacing(12)
        tata_kiri.addWidget(self.sampul)
        tata_kiri.addLayout(teks, 1)

        # Tengah: tombol kendali + progres
        self.tombol_acak = TombolIkon("acak", "Acak", 18, 32)
        self.tombol_sebelum = TombolIkon("sebelum", "Sebelumnya (Ctrl+←)", 18, 32)
        self.tombol_putar = TombolBulat(36, TEKS, "Putar / jeda (Spasi)")
        self.tombol_lanjut = TombolIkon("berikut", "Berikutnya (Ctrl+→)", 18, 32)
        self.tombol_ulang = TombolIkon("ulang", "Ulang", 18, 32)
        baris_tombol = QHBoxLayout()
        baris_tombol.setSpacing(16)
        baris_tombol.addStretch()
        for tombol in (self.tombol_acak, self.tombol_sebelum, self.tombol_putar, self.tombol_lanjut, self.tombol_ulang):
            baris_tombol.addWidget(tombol)
        baris_tombol.addStretch()

        self.label_posisi = label("0:00", "kecil")
        self.label_posisi.setFixedWidth(40)
        self.label_posisi.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.slider_posisi = QSlider(Qt.Horizontal)
        self.slider_posisi.setCursor(Qt.PointingHandCursor)
        self.label_durasi = label("0:00", "kecil")
        self.label_durasi.setFixedWidth(40)
        baris_posisi = QHBoxLayout()
        baris_posisi.setSpacing(8)
        baris_posisi.addWidget(self.label_posisi)
        baris_posisi.addWidget(self.slider_posisi, 1)
        baris_posisi.addWidget(self.label_durasi)
        tengah = QWidget()
        tengah.setMaximumWidth(640)
        tata_tengah = QVBoxLayout(tengah)
        tata_tengah.setContentsMargins(0, 8, 0, 8)
        tata_tengah.setSpacing(4)
        tata_tengah.addLayout(baris_tombol)
        tata_tengah.addLayout(baris_posisi)

        # Kanan: panel sedang diputar, antrean, volume
        self.tombol_diputar = TombolIkon("sedang_diputar", "Sedang diputar", 18, 32)
        self.tombol_antrean = TombolIkon("antrean", "Antrean", 18, 32)
        ikon_volume = QLabel()
        ikon_volume.setPixmap(pixmap_ikon("volume", TEKS_REDUP, 18))
        self.slider_volume = QSlider(Qt.Horizontal, maximum=100, value=VOLUME_AWAL)
        self.slider_volume.setFixedWidth(100)
        self.slider_volume.setCursor(Qt.PointingHandCursor)
        kanan = QWidget()
        tata_kanan = QHBoxLayout(kanan)
        tata_kanan.setContentsMargins(0, 0, 0, 0)
        tata_kanan.setSpacing(6)
        tata_kanan.addStretch()
        tata_kanan.addWidget(self.tombol_diputar)
        tata_kanan.addWidget(self.tombol_antrean)
        tata_kanan.addSpacing(6)
        tata_kanan.addWidget(ikon_volume)
        tata_kanan.addWidget(self.slider_volume)

        # Kolom kiri & kanan sama lebar agar kendali benar-benar di tengah.
        for widget in (kiri, kanan):
            widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        grid = QGridLayout(self)
        grid.setContentsMargins(8, 0, 8, 0)
        grid.setHorizontalSpacing(16)
        grid.addWidget(kiri, 0, 0)
        grid.addWidget(tengah, 0, 1)
        grid.addWidget(kanan, 0, 2)
        grid.setColumnStretch(0, 10)
        grid.setColumnStretch(1, 13)
        grid.setColumnStretch(2, 10)

    def _sambungkan_sinyal(self):
        p = self.pemutar
        self.tombol_putar.clicked.connect(p.putar_jeda)
        self.tombol_lanjut.clicked.connect(p.berikutnya)
        self.tombol_sebelum.clicked.connect(p.sebelumnya)
        self.tombol_acak.clicked.connect(lambda: p.atur_acak(not p.antrean.acak))
        self.tombol_ulang.clicked.connect(p.ganti_mode_ulang)
        p.mode_berubah.connect(self._segarkan_mode)
        self.tombol_diputar.clicked.connect(lambda: self.panel_diminta.emit("diputar"))
        self.tombol_antrean.clicked.connect(lambda: self.panel_diminta.emit("antrean"))
        self.slider_volume.valueChanged.connect(p.atur_volume)
        self.slider_posisi.sliderPressed.connect(lambda: setattr(self, "_sedang_geser", True))
        self.slider_posisi.sliderReleased.connect(self._selesai_geser)

        p.lagu_berubah.connect(self._tampilkan_lagu)
        p.status_berubah.connect(self.tombol_putar.atur_main)
        p.posisi_berubah.connect(self._posisi_berubah)
        p.durasi_berubah.connect(self._durasi_berubah)

    def _segarkan_mode(self):
        """Tombol acak/ulang yang aktif diberi warna aksen, seperti di Spotify."""
        antrean = self.pemutar.antrean
        self.tombol_acak.ganti_ikon("acak", AKSEN if antrean.acak else TEKS_REDUP)
        self.tombol_acak.setToolTip("Acak: aktif" if antrean.acak else "Acak: mati")
        self.tombol_ulang.ganti_ikon("ulang_satu" if antrean.ulang == ULANG_SATU else "ulang",
                                     TEKS_REDUP if antrean.ulang == ULANG_MATI else AKSEN)
        self.tombol_ulang.setToolTip(f"Ulang: {antrean.ulang}")

    def atur_panel_aktif(self, mode):
        """Ikon panel yang sedang terbuka diberi warna aksen."""
        self.tombol_diputar.ganti_ikon("sedang_diputar", AKSEN if mode == "diputar" else TEKS_REDUP)
        self.tombol_antrean.ganti_ikon("antrean", AKSEN if mode == "antrean" else TEKS_REDUP)

    def _tampilkan_lagu(self, lagu):
        self.sampul.setVisible(lagu is not None)
        self.sampul.atur(lagu.sampul if lagu else "")
        self.label_judul.setText(lagu.judul if lagu else "")
        self.label_artis.setText(lagu.artis if lagu else "")

    def _posisi_berubah(self, posisi):
        if not self._sedang_geser:
            self.slider_posisi.setValue(posisi)
        self.label_posisi.setText(format_waktu(posisi))

    def _durasi_berubah(self, durasi):
        self.slider_posisi.setRange(0, durasi)
        self.label_durasi.setText(format_waktu(durasi))

    def _selesai_geser(self):
        self._sedang_geser = False
        self.pemutar.geser_ke(self.slider_posisi.value())
