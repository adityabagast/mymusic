"""Kontrol media Windows (SMTC): tombol media keyboard/headset & overlay media Windows ikut mengendalikan Pemutar.

Butuh paket winrt (lihat requirements.txt). Bila tidak terpasang atau bukan Windows, buat_kontrol_media()
mengembalikan None dan aplikasi tetap berjalan seperti biasa.
"""
import sys

from PySide6.QtCore import QObject, Signal

from mymusic.services.youtube import perbesar_sampul

try:
    from winrt.windows.foundation import Uri
    from winrt.windows.media import MediaPlaybackStatus, MediaPlaybackType, SystemMediaTransportControlsButton
    from winrt.windows.media.playback import MediaPlayer
    from winrt.windows.storage.streams import RandomAccessStreamReference
    TERSEDIA = sys.platform == "win32"
except ImportError:
    TERSEDIA = False


class KontrolMediaWindows(QObject):
    # Tombol ditekan di thread milik Windows; lewat Signal ini diteruskan dengan aman ke thread Qt.
    _tombol = Signal(object)

    def __init__(self, pemutar, parent=None):
        super().__init__(parent)
        self.pemutar = pemutar
        # Aplikasi desktop biasa mendapatkan SMTC lewat MediaPlayer WinRT. Pemutar bawaannya tidak dipakai
        # untuk memutar apa pun, jadi kendali otomatisnya dimatikan.
        self._pemain_winrt = MediaPlayer()
        self._pemain_winrt.command_manager.is_enabled = False
        self._smtc = self._pemain_winrt.system_media_transport_controls
        self._smtc.is_enabled = True
        self._smtc.is_play_enabled = self._smtc.is_pause_enabled = True
        self._smtc.is_next_enabled = self._smtc.is_previous_enabled = True
        self._tombol.connect(self._tombol_ditekan)
        self._token = self._smtc.add_button_pressed(lambda _, argumen: self._tombol.emit(argumen.button))
        pemutar.lagu_berubah.connect(self._lagu_berubah)
        pemutar.status_berubah.connect(self._status_berubah)
        self._lagu_berubah(pemutar.antrean.sekarang)

    def _tombol_ditekan(self, tombol):
        p = self.pemutar
        if tombol == SystemMediaTransportControlsButton.PLAY and not p.sedang_memutar():
            p.putar_jeda()
        elif tombol == SystemMediaTransportControlsButton.PAUSE and p.sedang_memutar():
            p.putar_jeda()
        elif tombol == SystemMediaTransportControlsButton.NEXT:
            p.berikutnya()
        elif tombol == SystemMediaTransportControlsButton.PREVIOUS:
            p.sebelumnya()

    def _lagu_berubah(self, lagu):
        tampilan = self._smtc.display_updater
        if lagu is None:
            tampilan.clear_all()
            tampilan.update()
            self._smtc.playback_status = MediaPlaybackStatus.STOPPED
            return
        tampilan.type = MediaPlaybackType.MUSIC
        tampilan.music_properties.title = lagu.judul
        tampilan.music_properties.artist = lagu.artis
        tampilan.music_properties.album_title = lagu.album
        url = perbesar_sampul(lagu.sampul, 544)
        tampilan.thumbnail = RandomAccessStreamReference.create_from_uri(Uri(url)) if url else None
        tampilan.update()
        self._status_berubah(self.pemutar.sedang_memutar())

    def _status_berubah(self, sedang_main):
        if self.pemutar.antrean.sekarang is not None:
            self._smtc.playback_status = MediaPlaybackStatus.PLAYING if sedang_main else MediaPlaybackStatus.PAUSED

    def lepas(self):
        """Dipanggil saat aplikasi ditutup: sesi media hilang dari overlay Windows."""
        self._smtc.remove_button_pressed(self._token)
        self._smtc.is_enabled = False


def buat_kontrol_media(pemutar, parent=None):
    """KontrolMediaWindows, atau None bila tidak tersedia (bukan Windows / paket winrt belum dipasang)."""
    if not TERSEDIA:
        return None
    try:
        return KontrolMediaWindows(pemutar, parent)
    except (OSError, RuntimeError):
        return None  # mis. Windows versi lama yang tidak punya SMTC
