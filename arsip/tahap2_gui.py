import sys

import yt_dlp
from PySide6.QtCore import QObject, QRunnable, QThreadPool, QUrl, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QPushButton, QSlider, QVBoxLayout, QWidget,
)

from tahap1_cari import cari_lagu

OPSI_YTDLP = {
    "format": "bestaudio[ext=m4a]/bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
}


def ambil_url_audio(video_id):
    """Meminta yt-dlp alamat stream audio sebuah lagu (tanpa mengunduh)."""
    with yt_dlp.YoutubeDL(OPSI_YTDLP) as ydl:
        info = ydl.extract_info(f"https://music.youtube.com/watch?v={video_id}", download=False)
    return info["url"]


def nama_artis(lagu):
    return ", ".join(a["name"] for a in lagu.get("artists", []))


def format_waktu(ms):
    detik = ms // 1000
    return f"{detik // 60}:{detik % 60:02}"


class SinyalPekerja(QObject):
    selesai = Signal(object)
    gagal = Signal(str)


class Pekerja(QRunnable):
    """Menjalankan fungsi lambat (jaringan) di thread lain agar jendela tidak macet."""

    def __init__(self, fungsi, *args):
        super().__init__()
        self.fungsi = fungsi
        self.args = args
        self.sinyal = SinyalPekerja()

    def run(self):
        try:
            hasil = self.fungsi(*self.args)
        except Exception as e:
            self.sinyal.gagal.emit(str(e))
        else:
            self.sinyal.selesai.emit(hasil)


class JendelaUtama(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyMusic")
        self.resize(560, 640)

        self.pool = QThreadPool.globalInstance()
        self.jaringan = QNetworkAccessManager(self)
        self.daftar_lagu = []
        self.indeks_putar = -1
        self.lagu_putar = None
        self.nomor_permintaan = 0  # untuk mengabaikan hasil permintaan yang sudah basi
        self.sedang_geser = False

        self.pemutar = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.pemutar.setAudioOutput(self.audio)
        self.audio.setVolume(0.7)

        self._buat_tampilan()
        self._sambungkan_sinyal()

    # ---------- tampilan ----------

    def _buat_tampilan(self):
        self.kotak_cari = QLineEdit(placeholderText="Cari lagu, artis, atau album...")
        self.tombol_cari = QPushButton("Cari")
        baris_cari = QHBoxLayout()
        baris_cari.addWidget(self.kotak_cari)
        baris_cari.addWidget(self.tombol_cari)

        self.daftar = QListWidget()
        self.daftar.setAlternatingRowColors(True)

        self.sampul = QLabel()
        self.sampul.setFixedSize(64, 64)
        self.sampul.setScaledContents(True)
        self.sampul.setStyleSheet("background: #333; border-radius: 4px;")
        self.label_judul = QLabel("Belum ada lagu diputar")
        self.label_judul.setStyleSheet("font-weight: bold;")
        self.label_artis = QLabel("")
        info = QVBoxLayout()
        info.addWidget(self.label_judul)
        info.addWidget(self.label_artis)
        baris_info = QHBoxLayout()
        baris_info.addWidget(self.sampul)
        baris_info.addLayout(info, 1)

        self.label_posisi = QLabel("0:00")
        self.slider_posisi = QSlider(Qt.Horizontal)
        self.label_durasi = QLabel("0:00")
        baris_posisi = QHBoxLayout()
        baris_posisi.addWidget(self.label_posisi)
        baris_posisi.addWidget(self.slider_posisi, 1)
        baris_posisi.addWidget(self.label_durasi)

        self.tombol_sebelum = QPushButton("⏮")
        self.tombol_putar = QPushButton("▶")
        self.tombol_lanjut = QPushButton("⏭")
        for tombol in (self.tombol_sebelum, self.tombol_putar, self.tombol_lanjut):
            tombol.setFixedWidth(48)
        self.slider_volume = QSlider(Qt.Horizontal, maximum=100, value=70)
        self.slider_volume.setFixedWidth(110)
        baris_kontrol = QHBoxLayout()
        baris_kontrol.addStretch()
        baris_kontrol.addWidget(self.tombol_sebelum)
        baris_kontrol.addWidget(self.tombol_putar)
        baris_kontrol.addWidget(self.tombol_lanjut)
        baris_kontrol.addStretch()
        baris_kontrol.addWidget(QLabel("🔊"))
        baris_kontrol.addWidget(self.slider_volume)

        tata = QVBoxLayout()
        tata.addLayout(baris_cari)
        tata.addWidget(self.daftar, 1)
        tata.addLayout(baris_info)
        tata.addLayout(baris_posisi)
        tata.addLayout(baris_kontrol)
        wadah = QWidget()
        wadah.setLayout(tata)
        self.setCentralWidget(wadah)

    def _sambungkan_sinyal(self):
        self.kotak_cari.returnPressed.connect(self.mulai_cari)
        self.tombol_cari.clicked.connect(self.mulai_cari)
        self.daftar.itemActivated.connect(lambda item: self.putar_indeks(self.daftar.row(item)))

        self.tombol_putar.clicked.connect(self.putar_jeda)
        self.tombol_lanjut.clicked.connect(lambda: self.putar_indeks(self.indeks_putar + 1))
        self.tombol_sebelum.clicked.connect(self.sebelumnya)
        self.slider_volume.valueChanged.connect(lambda v: self.audio.setVolume(v / 100))

        self.slider_posisi.sliderPressed.connect(lambda: setattr(self, "sedang_geser", True))
        self.slider_posisi.sliderReleased.connect(self.selesai_geser)

        self.pemutar.positionChanged.connect(self.posisi_berubah)
        self.pemutar.durationChanged.connect(self.durasi_berubah)
        self.pemutar.playbackStateChanged.connect(self.status_putar_berubah)
        self.pemutar.mediaStatusChanged.connect(self.status_media_berubah)
        self.pemutar.errorOccurred.connect(lambda _, pesan: self.statusBar().showMessage(f"Gagal memutar: {pesan}"))

    # ---------- pencarian ----------

    def mulai_cari(self):
        kata = self.kotak_cari.text().strip()
        if not kata:
            return
        self.tombol_cari.setEnabled(False)
        self.statusBar().showMessage(f"Mencari \"{kata}\"...")
        pekerja = Pekerja(cari_lagu, kata)
        pekerja.sinyal.selesai.connect(self.tampilkan_hasil)
        pekerja.sinyal.gagal.connect(self.cari_gagal)
        self.pool.start(pekerja)

    def tampilkan_hasil(self, hasil):
        self.tombol_cari.setEnabled(True)
        # Hanya simpan lagu yang punya videoId, karena itu yang bisa diputar.
        self.daftar_lagu = [lagu for lagu in hasil if lagu.get("videoId")]
        self.indeks_putar = -1
        self.daftar.clear()
        for nomor, lagu in enumerate(self.daftar_lagu, start=1):
            teks = f"{nomor:2}. {lagu['title']} — {nama_artis(lagu)}  ({lagu.get('duration', '?')})"
            self.daftar.addItem(QListWidgetItem(teks))
        self.statusBar().showMessage(f"{len(self.daftar_lagu)} lagu ditemukan. Klik dua kali untuk memutar.")

    def cari_gagal(self, pesan):
        self.tombol_cari.setEnabled(True)
        self.statusBar().showMessage(f"Pencarian gagal: {pesan}")

    # ---------- pemutaran ----------

    def putar_indeks(self, indeks):
        if not 0 <= indeks < len(self.daftar_lagu):
            return
        self.indeks_putar = indeks
        self.daftar.setCurrentRow(indeks)
        lagu = self.daftar_lagu[indeks]
        self.lagu_putar = lagu

        self.pemutar.stop()
        self.label_judul.setText(lagu["title"])
        self.label_artis.setText(nama_artis(lagu))
        self.muat_sampul(lagu)
        self.statusBar().showMessage("Menyiapkan audio...")

        self.nomor_permintaan += 1
        nomor = self.nomor_permintaan
        pekerja = Pekerja(ambil_url_audio, lagu["videoId"])
        pekerja.sinyal.selesai.connect(lambda url: self.mulai_putar(nomor, url))
        pekerja.sinyal.gagal.connect(lambda pesan: self.statusBar().showMessage(f"Gagal mengambil audio: {pesan}"))
        self.pool.start(pekerja)

    def mulai_putar(self, nomor, url):
        if nomor != self.nomor_permintaan:
            return  # pengguna sudah memilih lagu lain
        self.pemutar.setSource(QUrl(url))
        self.pemutar.play()
        self.statusBar().clearMessage()

    def putar_jeda(self):
        if self.pemutar.playbackState() == QMediaPlayer.PlayingState:
            self.pemutar.pause()
        elif self.pemutar.source().isEmpty():
            self.putar_indeks(max(self.daftar.currentRow(), 0))
        else:
            self.pemutar.play()

    def sebelumnya(self):
        # Seperti pemutar musik umumnya: kalau sudah lewat 3 detik, ulang dari awal.
        if self.pemutar.position() > 3000:
            self.pemutar.setPosition(0)
        else:
            self.putar_indeks(self.indeks_putar - 1)

    def muat_sampul(self, lagu):
        self.sampul.clear()
        thumbnails = lagu.get("thumbnails") or []
        if not thumbnails:
            return
        balasan = self.jaringan.get(QNetworkRequest(QUrl(thumbnails[-1]["url"])))
        balasan.finished.connect(lambda: self.sampul_siap(balasan, lagu))

    def sampul_siap(self, balasan, lagu):
        balasan.deleteLater()
        if balasan.error() != QNetworkReply.NoError or self.lagu_putar is not lagu:
            return
        gambar = QPixmap()
        gambar.loadFromData(balasan.readAll())
        self.sampul.setPixmap(gambar)

    # ---------- status pemutar ----------

    def posisi_berubah(self, posisi):
        if not self.sedang_geser:
            self.slider_posisi.setValue(posisi)
        self.label_posisi.setText(format_waktu(posisi))

    def durasi_berubah(self, durasi):
        self.slider_posisi.setRange(0, durasi)
        self.label_durasi.setText(format_waktu(durasi))

    def selesai_geser(self):
        self.sedang_geser = False
        self.pemutar.setPosition(self.slider_posisi.value())

    def status_putar_berubah(self, status):
        self.tombol_putar.setText("⏸" if status == QMediaPlayer.PlayingState else "▶")

    def status_media_berubah(self, status):
        if status == QMediaPlayer.BufferingMedia:
            self.statusBar().showMessage("Buffering...")
        elif status == QMediaPlayer.BufferedMedia:
            self.statusBar().clearMessage()
        elif status == QMediaPlayer.EndOfMedia:
            self.putar_indeks(self.indeks_putar + 1)  # lanjut otomatis ke lagu berikutnya


def main():
    app = QApplication(sys.argv)
    jendela = JendelaUtama()
    jendela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
