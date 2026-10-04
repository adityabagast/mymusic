"""Mengunduh gambar sampul sekali saja, lalu menyimpannya di memori."""
from PySide6.QtCore import QObject, QUrl
from PySide6.QtGui import QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest


class PemuatSampul(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._jaringan = QNetworkAccessManager(self)
        self._cache = {}  # url -> QPixmap
        self._menunggu = {}  # url -> [callback, ...]

    def muat(self, url, callback):
        """Memanggil callback(QPixmap) setelah gambar siap (langsung, bila sudah ada di cache)."""
        if not url:
            return
        if url in self._cache:
            callback(self._cache[url])
            return
        if url in self._menunggu:  # sedang diunduh, cukup ikut menunggu
            self._menunggu[url].append(callback)
            return
        self._menunggu[url] = [callback]
        balasan = self._jaringan.get(QNetworkRequest(QUrl(url)))
        balasan.finished.connect(lambda: self._selesai(url, balasan))

    def _selesai(self, url, balasan):
        balasan.deleteLater()
        callbacks = self._menunggu.pop(url, [])
        if balasan.error() != QNetworkReply.NoError:
            return
        gambar = QPixmap()
        if not gambar.loadFromData(balasan.readAll()):
            return
        self._cache[url] = gambar
        for callback in callbacks:
            try:
                callback(gambar)
            except RuntimeError:
                pass  # widget peminta sudah dihapus (mis. daftar lagu sudah diganti)


_pemuat = None


def pemuat_sampul():
    """Satu PemuatSampul untuk seluruh aplikasi (dibuat saat pertama dipakai)."""
    global _pemuat
    if _pemuat is None:
        _pemuat = PemuatSampul()
    return _pemuat