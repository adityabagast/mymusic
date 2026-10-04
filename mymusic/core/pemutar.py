"""Pemutar = QMediaPlayer + Antrean. Tampilan cukup memanggil metode di sini
dan mendengarkan sinyalnya, tanpa perlu tahu soal yt-dlp atau QMediaPlayer."""
import random

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

from mymusic.config import VOLUME_AWAL
from mymusic.core.antrean import ULANG_MATI, ULANG_SATU, ULANG_SEMUA, Antrean
from mymusic.core.pekerja import jalankan_di_latar
from mymusic.services.youtube import ambil_url_audio


class Pemutar(QObject):
    lagu_berubah = Signal(object)  # Lagu, atau None bila berhenti
    antrean_berubah = Signal()
    mode_berubah = Signal()  # acak / ulang berubah
    status_berubah = Signal(bool)  # True = sedang memutar
    posisi_berubah = Signal(int)  # milidetik
    durasi_berubah = Signal(int)  # milidetik
    pesan = Signal(str)  # teks untuk status bar

    def __init__(self, parent=None):
        super().__init__(parent)
        self.antrean = Antrean()
        self.sumber = ""  # nama asal antrean, mis. nama playlist atau "Hasil cari ..."
        self._nomor_permintaan = 0  # untuk mengabaikan URL yang datang terlambat
        self._posisi_tunda = 0  # posisi (ms) yang dituju setelah lagu selesai dimuat
        self._posisi_tersimpan = 0  # posisi lagu dari sesi sebelumnya, dipakai saat tombol putar ditekan
        self._sudah_coba_ulang = False  # URL baru sudah dicoba sekali untuk lagu ini

        self._player = QMediaPlayer(self)
        self._audio = QAudioOutput(self)
        self._player.setAudioOutput(self._audio)
        self.atur_volume(VOLUME_AWAL)

        self._player.positionChanged.connect(self.posisi_berubah.emit)
        self._player.durationChanged.connect(self.durasi_berubah.emit)
        self._player.playbackStateChanged.connect(
            lambda status: self.status_berubah.emit(status == QMediaPlayer.PlayingState))
        self._player.mediaStatusChanged.connect(self._status_media_berubah)
        self._player.errorOccurred.connect(self._gagal_memutar)

    # ---------- kendali antrean ----------

    def putar_daftar(self, daftar_lagu, mulai=None, sumber=""):
        """Ganti seluruh antrean dengan daftar_lagu lalu putar dari posisi `mulai`.

        Tanpa `mulai`, putar dari awal — atau dari lagu acak bila mode acak aktif.
        """
        if not daftar_lagu:
            return
        if mulai is None:
            mulai = random.randrange(len(daftar_lagu)) if self.antrean.acak else 0
        self.sumber = sumber
        self.antrean.ganti_semua(daftar_lagu, mulai)
        self.antrean_berubah.emit()
        self._putar_lagu_sekarang()

    def tambah(self, daftar_lagu):
        for lagu in daftar_lagu:
            self.antrean.tambah(lagu)
        self.antrean_berubah.emit()

    def sisipkan_berikutnya(self, daftar_lagu):
        for lagu in reversed(daftar_lagu):  # dibalik agar urutannya tetap sama
            self.antrean.sisipkan_berikutnya(lagu)
        self.antrean_berubah.emit()

    def hapus(self, daftar_posisi):
        lagu_diputar_dihapus = self.antrean.indeks in daftar_posisi
        for posisi in sorted(daftar_posisi, reverse=True):  # dari belakang agar posisi tidak bergeser
            self.antrean.hapus(posisi)
        self.antrean_berubah.emit()
        if lagu_diputar_dihapus:
            self._putar_lagu_sekarang()  # lanjut ke lagu yang kini menempati posisinya

    def kosongkan(self):
        self.antrean.kosongkan()
        self._berhenti()
        self.antrean_berubah.emit()

    def pindahkan(self, dari, ke):
        self.antrean.pindahkan(dari, ke)
        self.antrean_berubah.emit()

    def putar_di(self, posisi):
        if self.antrean.pindah_ke(posisi):
            self._putar_lagu_sekarang()

    def berikutnya(self):
        if self.antrean.berikutnya():
            self._putar_lagu_sekarang()

    def sebelumnya(self):
        # Seperti pemutar musik umumnya: kalau sudah lewat 3 detik, ulang dari awal.
        if self._player.position() > 3000:
            self._player.setPosition(0)
        elif self.antrean.sebelumnya():
            self._putar_lagu_sekarang()

    # ---------- kendali pemutaran ----------

    def putar_jeda(self):
        if self._player.playbackState() == QMediaPlayer.PlayingState:
            self._player.pause()
        elif not self._player.source().isEmpty():
            self._player.play()
        elif self.antrean.pindah_ke(max(self.antrean.indeks, 0)):
            # Belum ada audio dimuat (mis. baru membuka aplikasi): lanjutkan dari posisi sesi sebelumnya.
            self._putar_lagu_sekarang(self._posisi_tersimpan)

    def sedang_memutar(self):
        return self._player.playbackState() == QMediaPlayer.PlayingState

    def geser_ke(self, milidetik):
        self._player.setPosition(milidetik)

    def geser_relatif(self, milidetik):
        """Maju (positif) atau mundur (negatif) beberapa milidetik."""
        if not self._player.source().isEmpty():
            self._player.setPosition(max(0, self._player.position() + milidetik))

    # ---------- mode acak & ulang ----------

    def atur_acak(self, aktif):
        self.antrean.atur_acak(aktif)
        self.mode_berubah.emit()
        self.antrean_berubah.emit()

    def ganti_mode_ulang(self):
        """Berputar: mati -> semua -> satu -> mati."""
        urutan = [ULANG_MATI, ULANG_SEMUA, ULANG_SATU]
        self.antrean.ulang = urutan[(urutan.index(self.antrean.ulang) + 1) % len(urutan)]
        self.mode_berubah.emit()

    # ---------- sesi (dipulihkan saat aplikasi dibuka lagi) ----------

    def ke_sesi(self):
        sesi = self.antrean.ke_dict()
        sesi["sumber"] = self.sumber
        sesi["posisi"] = self._player.position() if not self._player.source().isEmpty() else self._posisi_tersimpan
        return sesi

    def pulihkan_sesi(self, sesi):
        """Mengisi antrean dari sesi sebelumnya tanpa langsung memutar."""
        self.antrean.muat_dict(sesi)
        self.sumber = sesi.get("sumber", "")
        self._posisi_tersimpan = sesi.get("posisi", 0)
        self.antrean_berubah.emit()
        self.mode_berubah.emit()
        lagu = self.antrean.sekarang
        self.lagu_berubah.emit(lagu)
        if lagu:
            self.durasi_berubah.emit(lagu.detik * 1000)
            self.posisi_berubah.emit(self._posisi_tersimpan)

    def atur_volume(self, persen):
        self._audio.setVolume(persen / 100)

    # ---------- bagian dalam ----------

    def _putar_lagu_sekarang(self, posisi_awal=0):
        self._sudah_coba_ulang = False
        self._posisi_tunda = posisi_awal
        self._posisi_tersimpan = 0
        lagu = self.antrean.sekarang
        if lagu is None:
            self._berhenti()
            return
        self._player.stop()
        self.lagu_berubah.emit(lagu)
        self.pesan.emit("Menyiapkan audio...")

        self._nomor_permintaan += 1
        nomor = self._nomor_permintaan
        jalankan_di_latar(
            ambil_url_audio, lagu.video_id,
            selesai=lambda url: self._mulai_stream(nomor, url),
            gagal=lambda pesan: self.pesan.emit(f"Gagal mengambil audio: {pesan}"),
        )

    def _mulai_stream(self, nomor, url):
        if nomor != self._nomor_permintaan:
            return  # pengguna sudah memilih lagu lain
        self._player.setSource(QUrl(url))
        self._player.play()
        self.pesan.emit("")

    def _berhenti(self):
        self._nomor_permintaan += 1  # batalkan URL yang mungkin masih dalam perjalanan
        self._player.stop()
        self._player.setSource(QUrl())
        self.lagu_berubah.emit(None)

    def _gagal_memutar(self, _, pesan):
        # Server YouTube sesekali menolak (HTTP 403) atau URL-nya kedaluwarsa:
        # minta URL baru sekali, lalu lanjutkan dari posisi yang sama.
        if not self._sudah_coba_ulang and self.antrean.sekarang:
            self._putar_lagu_sekarang(self._player.position())
            self._sudah_coba_ulang = True
            return
        self.pesan.emit(f"Gagal memutar: {pesan}")

    def _status_media_berubah(self, status):
        if status in (QMediaPlayer.LoadedMedia, QMediaPlayer.BufferedMedia) and self._posisi_tunda:
            self._player.setPosition(self._posisi_tunda)  # baru bisa digeser setelah lagu dimuat
            self._posisi_tunda = 0
        if status == QMediaPlayer.BufferingMedia:
            self.pesan.emit("Buffering...")
        elif status == QMediaPlayer.BufferedMedia:
            self.pesan.emit("")
        elif status == QMediaPlayer.EndOfMedia:
            if self.antrean.ulang == ULANG_SATU:
                self._player.setPosition(0)
                self._player.play()
            else:
                self.berikutnya()  # lanjut otomatis (kembali ke awal bila ulang semua)