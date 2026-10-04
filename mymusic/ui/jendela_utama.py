"""Jendela utama: merangkai bilah atas, Koleksi, halaman tengah, panel kanan, dan bilah pemutar."""
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QHBoxLayout, QInputDialog, QMainWindow, QMessageBox, QStackedWidget, QVBoxLayout, QWidget

from mymusic.config import LANGKAH_GESER_MS, LANGKAH_VOLUME, NAMA_APLIKASI, VOLUME_AWAL
from mymusic.core.pekerja import jalankan_di_latar
from mymusic.core.pemutar import Pemutar
from mymusic.services.penyimpanan import PenyimpananPlaylist
from mymusic.services.sesi import PenyimpananSesi
from mymusic.services.youtube import (
    adalah_link, ambil_id_playlist, ambil_lirik, ambil_playlist, ambil_playlist_rekomendasi, ambil_rekomendasi_lagu,
    cari_lagu,
)
from mymusic.ui.bilah_atas import BilahAtas
from mymusic.ui.bilah_pemutar import BilahPemutar
from mymusic.ui.halaman_beranda import HalamanBeranda
from mymusic.ui.halaman_cari import HalamanCari
from mymusic.ui.halaman_lirik import HalamanLirik
from mymusic.ui.halaman_playlist import SAYA, YOUTUBE, HalamanPlaylist
from mymusic.ui.panel_kanan import DIPUTAR, PanelKanan
from mymusic.ui.panel_koleksi import PanelKoleksi
from mymusic.ui.widgets import PanelBulat, Toast


class JendelaUtama(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(NAMA_APLIKASI)
        self.resize(1280, 820)
        self.setMinimumSize(1080, 680)

        self.pemutar = Pemutar(self)
        self.penyimpanan = PenyimpananPlaylist()
        self.penyimpanan_sesi = PenyimpananSesi()
        self.hasil_cari = []
        self.kata_cari = ""
        self.isi_playlist = []  # lagu yang tampil di halaman playlist
        self._nomor_permintaan = 0  # untuk mengabaikan hasil cari/playlist yang sudah basi
        self._id_rekomendasi = None
        self._halaman_sebelum_lirik = None

        self._buat_tampilan()
        self._sambungkan_sinyal()
        self._pasang_pintasan()
        self._segarkan_koleksi()
        self._pulihkan_sesi()
        jalankan_di_latar(ambil_playlist_rekomendasi,
                          selesai=self.beranda.tampilkan_playlist_rekomendasi,
                          gagal=self.beranda.tampilkan_gagal_playlist)

    # ---------- tampilan ----------

    def _buat_tampilan(self):
        self.bilah_atas = BilahAtas()
        self.koleksi = PanelKoleksi()
        self.beranda = HalamanBeranda()
        self.halaman_cari = HalamanCari()
        self.halaman_playlist = HalamanPlaylist()
        self.halaman_lirik = HalamanLirik()
        self.tumpukan = QStackedWidget()
        for halaman in (self.beranda, self.halaman_cari, self.halaman_playlist, self.halaman_lirik):
            self.tumpukan.addWidget(halaman)
        pusat = PanelBulat()
        tata_pusat = QVBoxLayout(pusat)
        tata_pusat.setContentsMargins(0, 0, 0, 0)
        tata_pusat.addWidget(self.tumpukan)
        self.panel_kanan = PanelKanan(self.pemutar)
        self.bilah_pemutar = BilahPemutar(self.pemutar)

        tubuh = QHBoxLayout()
        tubuh.setSpacing(8)
        tubuh.addWidget(self.koleksi)
        tubuh.addWidget(pusat, 1)
        tubuh.addWidget(self.panel_kanan)

        wadah = QWidget()
        wadah.setObjectName("wadah")
        tata = QVBoxLayout(wadah)
        tata.setContentsMargins(8, 0, 8, 0)
        tata.setSpacing(0)
        tata.addWidget(self.bilah_atas)
        tata.addLayout(tubuh, 1)
        tata.addWidget(self.bilah_pemutar)
        self.setCentralWidget(wadah)
        self.toast = Toast(wadah)

    def _sambungkan_sinyal(self):
        self.bilah_atas.cari.connect(self.mulai_cari)
        self.bilah_atas.beranda.connect(lambda: self.tampilkan_halaman(self.beranda))

        self.koleksi.buka.connect(self.buka_playlist_saya)
        self.koleksi.putar.connect(self.putar_playlist_saya)
        self.koleksi.simpan_antrean.connect(self.simpan_antrean)

        b = self.beranda
        b.buka_playlist_saya.connect(self.buka_playlist_saya)
        b.putar_playlist_saya.connect(self.putar_playlist_saya)
        b.buka_playlist_yt.connect(lambda info: self.buka_playlist_yt(info.id, info.judul))
        b.putar_playlist_yt.connect(lambda info: self.buka_playlist_yt(info.id, info.judul, putar=True))
        b.putar_rekomendasi.connect(
            lambda i: self.pemutar.putar_daftar(b.rekomendasi_lagu, i, b.judul_rekomendasi))
        b.minta_tempel_link.connect(self._minta_tempel_link)

        c = self.halaman_cari
        c.putar.connect(lambda i: self.pemutar.putar_daftar(self.hasil_cari, i, f"Hasil cari “{self.kata_cari}”"))
        c.tambah.connect(self.tambah_ke_antrean)
        c.sisipkan.connect(self.sisipkan_ke_antrean)

        p = self.halaman_playlist
        p.putar.connect(lambda i: self.pemutar.putar_daftar(self.isi_playlist, i, p.judul))
        p.putar_jeda.connect(self.klik_putar_playlist)
        p.tambah.connect(self.tambah_ke_antrean)
        p.sisipkan.connect(self.sisipkan_ke_antrean)
        p.tambah_semua.connect(self.tambah_semua_ke_antrean)
        p.simpan.connect(self.simpan_playlist_yt)
        p.hapus.connect(self.hapus_playlist_saya)
        p.acak.connect(lambda: self.pemutar.atur_acak(not self.pemutar.antrean.acak))

        self.panel_kanan.tutup.connect(lambda: self.tampilkan_panel(None))
        self.panel_kanan.simpan_antrean.connect(self.simpan_antrean)
        self.bilah_pemutar.panel_diminta.connect(self._alihkan_panel)
        self.bilah_pemutar.lirik_diminta.connect(self._alihkan_lirik)
        self.halaman_lirik.geser.connect(self.pemutar.geser_ke)
        self.pemutar.posisi_berubah.connect(self.halaman_lirik.atur_posisi)

        self.pemutar.lagu_berubah.connect(self._lagu_berubah)
        self.pemutar.mode_berubah.connect(lambda: self.halaman_playlist.atur_acak(self.pemutar.antrean.acak))
        self.pemutar.status_berubah.connect(lambda _: self._segarkan_tombol_playlist())
        self.pemutar.pesan.connect(lambda pesan: pesan.startswith("Gagal") and self.toast.tampilkan(pesan))

    def _pasang_pintasan(self):
        """Pintasan keyboard. Saat mengetik di kotak cari, tombol-tombol ini tetap dipakai untuk mengetik."""
        p = self.pemutar
        pintasan = {
            "Space": p.putar_jeda,
            "Ctrl+Right": p.berikutnya,
            "Ctrl+Left": p.sebelumnya,
            "Shift+Right": lambda: p.geser_relatif(LANGKAH_GESER_MS),
            "Shift+Left": lambda: p.geser_relatif(-LANGKAH_GESER_MS),
            "Ctrl+Up": lambda: self._ubah_volume(LANGKAH_VOLUME),
            "Ctrl+Down": lambda: self._ubah_volume(-LANGKAH_VOLUME),
            "Ctrl+F": self.bilah_atas.fokus_cari,
            "Ctrl+S": lambda: p.atur_acak(not p.antrean.acak),
            "Ctrl+R": p.ganti_mode_ulang,
        }
        for tombol, aksi in pintasan.items():
            QShortcut(QKeySequence(tombol), self).activated.connect(aksi)

    def _ubah_volume(self, selisih):
        slider = self.bilah_pemutar.slider_volume
        slider.setValue(slider.value() + selisih)

    # ---------- sesi ----------

    def _pulihkan_sesi(self):
        sesi = self.penyimpanan_sesi.baca()
        self.bilah_pemutar.slider_volume.setValue(sesi.get("volume", VOLUME_AWAL))
        self.tampilkan_panel(sesi.get("panel", DIPUTAR))
        try:
            self.pemutar.pulihkan_sesi(sesi.get("pemutar", {}))
        except (KeyError, TypeError, ValueError):
            pass  # sesi lama tidak cocok dengan format sekarang: mulai dari kosong saja

    def closeEvent(self, event):
        self.penyimpanan_sesi.simpan({
            "volume": self.bilah_pemutar.slider_volume.value(),
            "panel": self.panel_kanan.mode(),
            "pemutar": self.pemutar.ke_sesi(),
        })
        super().closeEvent(event)

    def tampilkan_halaman(self, halaman):
        self.tumpukan.setCurrentWidget(halaman)
        self.bilah_atas.atur_beranda_aktif(halaman is self.beranda)
        self.bilah_pemutar.atur_lirik_aktif(halaman is self.halaman_lirik)
        self._tandai_koleksi()

    def tampilkan_panel(self, mode):
        if mode is None:
            self.panel_kanan.hide()
        else:
            self.panel_kanan.tampilkan(mode)
        self.bilah_pemutar.atur_panel_aktif(mode)

    def _alihkan_panel(self, mode):
        self.tampilkan_panel(None if self.panel_kanan.mode() == mode else mode)

    def _alihkan_lirik(self):
        """Tombol lirik: buka halaman lirik, atau kembali ke halaman sebelumnya bila sudah terbuka."""
        if self.tumpukan.currentWidget() is self.halaman_lirik:
            self.tampilkan_halaman(self._halaman_sebelum_lirik or self.beranda)
            return
        self._halaman_sebelum_lirik = self.tumpukan.currentWidget()
        self.tampilkan_halaman(self.halaman_lirik)
        self._muat_lirik()

    def _muat_lirik(self):
        """Mengambil lirik lagu yang sedang diputar, hanya bila halaman lirik sedang terbuka."""
        if self.tumpukan.currentWidget() is not self.halaman_lirik:
            return
        lagu = self.pemutar.antrean.sekarang
        if lagu is None:
            self.halaman_lirik.tampilkan_kosong()
        elif lagu.video_id != self.halaman_lirik.video_id:  # belum dimuat untuk lagu ini
            self.halaman_lirik.tampilkan_memuat(lagu)
            jalankan_di_latar(ambil_lirik, lagu.video_id,
                              selesai=lambda lirik: self.halaman_lirik.tampilkan(lagu, lirik),
                              gagal=lambda pesan: self.halaman_lirik.tampilkan_gagal(lagu, pesan))

    def _minta_tempel_link(self):
        self.bilah_atas.fokus_cari()
        self.toast.tampilkan("Tempel link playlist YouTube di kotak cari, lalu tekan Enter.")

    # ---------- pencarian & link playlist ----------

    def mulai_cari(self, teks):
        if adalah_link(teks):
            id_playlist = ambil_id_playlist(teks)
            if id_playlist:
                self.buka_playlist_yt(id_playlist, "Playlist YouTube")
            else:
                self.toast.tampilkan("Link ini tidak berisi playlist (tidak ada bagian ?list=…).")
            return
        self._nomor_permintaan += 1
        nomor = self._nomor_permintaan
        self.tampilkan_halaman(self.halaman_cari)
        self.halaman_cari.tampilkan_memuat(teks)
        jalankan_di_latar(cari_lagu, teks,
                          selesai=lambda daftar: self._hasil_cari_siap(nomor, teks, daftar),
                          gagal=lambda pesan: self.halaman_cari.tampilkan_pesan(f"Pencarian gagal: {pesan}"))

    def _hasil_cari_siap(self, nomor, kata, daftar):
        if nomor != self._nomor_permintaan:
            return
        self.hasil_cari = daftar
        self.kata_cari = kata
        self.halaman_cari.tampilkan(kata, daftar, self.pemutar.antrean.sekarang)

    def buka_playlist_yt(self, id_playlist, judul_sementara, putar=False):
        self._nomor_permintaan += 1
        nomor = self._nomor_permintaan
        self.tampilkan_halaman(self.halaman_playlist)
        self.halaman_playlist.tampilkan_memuat(judul_sementara)
        self._tandai_koleksi()
        jalankan_di_latar(ambil_playlist, id_playlist,
                          selesai=lambda hasil: self._playlist_yt_siap(nomor, hasil, putar),
                          gagal=self.halaman_playlist.tampilkan_gagal)

    def _playlist_yt_siap(self, nomor, hasil, putar):
        if nomor != self._nomor_permintaan:
            return
        judul, daftar = hasil
        self.isi_playlist = daftar
        self.halaman_playlist.tampilkan(YOUTUBE, judul, daftar, self.pemutar.antrean.sekarang)
        if putar and daftar:
            self.pemutar.putar_daftar(daftar, sumber=judul)
        self._segarkan_tombol_playlist()

    # ---------- antrean ----------

    def tambah_ke_antrean(self, lagu):
        self.pemutar.tambah([lagu])
        self.toast.tampilkan("Ditambahkan ke antrean")

    def sisipkan_ke_antrean(self, lagu):
        self.pemutar.sisipkan_berikutnya([lagu])
        self.toast.tampilkan("Akan diputar berikutnya")

    def tambah_semua_ke_antrean(self):
        self.pemutar.tambah(self.isi_playlist)
        self.toast.tampilkan(f"{len(self.isi_playlist)} lagu ditambahkan ke antrean")

    def klik_putar_playlist(self):
        p = self.halaman_playlist
        if self.pemutar.sumber == p.judul and self.pemutar.antrean.sekarang:
            self.pemutar.putar_jeda()  # playlist ini sedang di antrean: cukup jeda/lanjutkan
        elif self.isi_playlist:
            self.pemutar.putar_daftar(self.isi_playlist, sumber=p.judul)

    def _segarkan_tombol_playlist(self):
        self.halaman_playlist.atur_main(
            self.pemutar.sedang_memutar() and self.pemutar.sumber == self.halaman_playlist.judul)

    def _lagu_berubah(self, lagu):
        self.halaman_cari.tandai(lagu)
        self.halaman_playlist.tandai(lagu)
        self._tandai_koleksi()
        self._segarkan_tombol_playlist()
        self._muat_lirik()
        if lagu and lagu.video_id != self._id_rekomendasi:
            self._id_rekomendasi = lagu.video_id
            jalankan_di_latar(ambil_rekomendasi_lagu, lagu.video_id,
                              selesai=lambda daftar: self._rekomendasi_siap(lagu, daftar))

    def _rekomendasi_siap(self, lagu, daftar):
        if lagu.video_id == self._id_rekomendasi:
            self.beranda.tampilkan_rekomendasi_lagu(lagu, daftar)

    # ---------- Koleksi Kamu (playlist tersimpan) ----------

    def _segarkan_koleksi(self):
        semua = [(nama, self.penyimpanan.ambil(nama)) for nama in self.penyimpanan.semua_nama()]
        self.koleksi.isi([(nama, f"Playlist · {len(lagu)} lagu", lagu[0].sampul if lagu else "")
                          for nama, lagu in semua])
        self.beranda.isi_pintasan([(nama, lagu[0].sampul if lagu else "") for nama, lagu in semua])
        self._tandai_koleksi()

    def _tandai_koleksi(self):
        p = self.halaman_playlist
        terbuka = p.judul if self.tumpukan.currentWidget() is p and p.jenis == SAYA else None
        diputar = self.pemutar.sumber if self.pemutar.antrean.sekarang else None
        self.koleksi.tandai(terbuka, diputar)

    def buka_playlist_saya(self, nama):
        self._nomor_permintaan += 1  # batalkan playlist YouTube yang mungkin masih dimuat
        self.isi_playlist = self.penyimpanan.ambil(nama)
        self.halaman_playlist.tampilkan(SAYA, nama, self.isi_playlist, self.pemutar.antrean.sekarang)
        self.tampilkan_halaman(self.halaman_playlist)
        self._segarkan_tombol_playlist()

    def putar_playlist_saya(self, nama):
        daftar = self.penyimpanan.ambil(nama)
        if daftar:
            self.pemutar.putar_daftar(daftar, sumber=nama)

    def _tanya_timpa(self, nama):
        if nama not in self.penyimpanan.semua_nama():
            return True
        jawab = QMessageBox.question(self, "Timpa playlist?", f"Playlist “{nama}” sudah ada. Timpa?")
        return jawab == QMessageBox.Yes

    def simpan_antrean(self):
        if not len(self.pemutar.antrean):
            self.toast.tampilkan("Antrean masih kosong")
            return
        nama, ok = QInputDialog.getText(self, "Simpan playlist", "Nama playlist:")
        nama = nama.strip()
        if not ok or not nama or not self._tanya_timpa(nama):
            return
        self.penyimpanan.simpan(nama, self.pemutar.antrean.lagu)
        self._segarkan_koleksi()
        self.toast.tampilkan(f"Disimpan sebagai “{nama}”")

    def simpan_playlist_yt(self):
        nama = self.halaman_playlist.judul
        if not self.isi_playlist or not self._tanya_timpa(nama):
            return
        self.penyimpanan.simpan(nama, self.isi_playlist)
        self._segarkan_koleksi()
        self.toast.tampilkan("Disimpan ke Koleksi Kamu")

    def hapus_playlist_saya(self):
        nama = self.halaman_playlist.judul
        if QMessageBox.question(self, "Hapus playlist?", f"Hapus playlist “{nama}”?") == QMessageBox.Yes:
            self.penyimpanan.hapus(nama)
            self._segarkan_koleksi()
            self.tampilkan_halaman(self.beranda)
            self.toast.tampilkan("Playlist dihapus")
