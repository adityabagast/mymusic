"""Memastikan MyMusic hanya berjalan satu kali: membuka lagi = menampilkan jendela yang sudah ada."""
import sys
from pathlib import Path

from PySide6.QtCore import QDir, QLockFile, QObject, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket


class SatuInstans(QObject):
    diminta_tampil = Signal()  # ada yang mencoba membuka MyMusic lagi

    def __init__(self, nama, parent=None):
        super().__init__(parent)
        self._nama = nama
        # Kunci file = penentu siapa yang pertama. Bila prosesnya mati mendadak, Qt tahu kuncinya basi.
        self._kunci = QLockFile(str(Path(QDir.tempPath()) / f"{nama}.lock"))
        self._server = None

    def jadi_utama(self):
        """True bila belum ada MyMusic lain; bila sudah ada, minta ia tampil lalu kembalikan False."""
        if not self._kunci.tryLock(0):
            self._panggil_instans_utama()
            return False
        self._server = QLocalServer(self)
        self._server.newConnection.connect(self._ada_panggilan)
        self._server.listen(self._nama)
        return True

    def _panggil_instans_utama(self):
        if sys.platform == "win32":
            # Windows hanya mengizinkan proses yang baru dibuka pengguna merebut fokus; izin itu kita berikan.
            import ctypes
            ctypes.windll.user32.AllowSetForegroundWindow(-1)  # -1 = ASFW_ANY
        soket = QLocalSocket()
        soket.connectToServer(self._nama)
        # Gagal pun tak apa: berarti instans utama masih dimulai, dan jendelanya toh akan muncul.
        soket.waitForConnected(1000)
        soket.disconnectFromServer()

    def _ada_panggilan(self):
        while self._server.hasPendingConnections():
            self._server.nextPendingConnection().deleteLater()
        self.diminta_tampil.emit()