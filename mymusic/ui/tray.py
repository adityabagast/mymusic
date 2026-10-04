"""Ikon MyMusic di system tray (pojok kanan bawah taskbar) beserta menu klik kanannya."""
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from mymusic.config import FILE_IKON, NAMA_APLIKASI
from mymusic.ui.ikon import ikon
from mymusic.ui.tema import TEKS_REDUP


class TrayAplikasi(QSystemTrayIcon):
    tampilkan_jendela = Signal()
    keluar = Signal()
    tutup_ke_tray_diubah = Signal(bool)

    def __init__(self, pemutar, parent=None):
        super().__init__(QIcon(str(FILE_IKON)), parent)
        self.pemutar = pemutar
        self._menu = QMenu()  # disimpan di atribut: QSystemTrayIcon tidak memegang kepemilikan menu
        self.aksi_lagu = self._menu.addAction("")
        self.aksi_lagu.setEnabled(False)  # hanya keterangan lagu yang sedang diputar
        self._menu.addSeparator()
        self.aksi_putar = self._menu.addAction("")
        self.aksi_putar.triggered.connect(pemutar.putar_jeda)
        self._menu.addAction(ikon("berikut", TEKS_REDUP, 16), "Berikutnya").triggered.connect(pemutar.berikutnya)
        self._menu.addAction(ikon("sebelum", TEKS_REDUP, 16), "Sebelumnya").triggered.connect(pemutar.sebelumnya)
        self._menu.addSeparator()
        self.aksi_tutup_ke_tray = self._menu.addAction("Tetap berjalan di sini saat jendela ditutup")
        self.aksi_tutup_ke_tray.setCheckable(True)
        self.aksi_tutup_ke_tray.toggled.connect(self.tutup_ke_tray_diubah.emit)
        self._menu.addAction(f"Tampilkan {NAMA_APLIKASI}").triggered.connect(self.tampilkan_jendela.emit)
        self._menu.addAction(f"Keluar dari {NAMA_APLIKASI}").triggered.connect(self.keluar.emit)
        self.setContextMenu(self._menu)

        self.activated.connect(self._diklik)
        pemutar.lagu_berubah.connect(self._lagu_berubah)
        pemutar.status_berubah.connect(self._status_berubah)
        self._lagu_berubah(pemutar.antrean.sekarang)
        self._status_berubah(False)

    def atur_tutup_ke_tray(self, aktif):
        self.aksi_tutup_ke_tray.setChecked(aktif)

    def _diklik(self, alasan):
        if alasan == QSystemTrayIcon.Trigger:  # klik kiri biasa
            self.tampilkan_jendela.emit()
        elif alasan == QSystemTrayIcon.MiddleClick:
            self.pemutar.putar_jeda()

    def _lagu_berubah(self, lagu):
        teks = f"{lagu.judul} — {lagu.artis}" if lagu else "Belum ada lagu diputar"
        self.aksi_lagu.setText(teks if len(teks) <= 60 else teks[:59] + "…")
        # Tooltip tray Windows dibatasi 127 karakter.
        self.setToolTip(f"{NAMA_APLIKASI}\n{teks}"[:127] if lagu else NAMA_APLIKASI)

    def _status_berubah(self, sedang_main):
        self.aksi_putar.setText("Jeda" if sedang_main else "Putar")
        self.aksi_putar.setIcon(ikon("jeda" if sedang_main else "putar", TEKS_REDUP, 16))
