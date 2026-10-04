"""Jendela utama: merangkai bilah atas, Koleksi, halaman tengah, panel kanan, dan bilah pemutar."""
import random

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QInputDialog, QMainWindow, QMessageBox, QStackedWidget, QVBoxLayout, QWidget,
)

from mymusic.config import (
    BATAS_RIWAYAT, FILE_RIWAYAT, LANGKAH_GESER_MS, LANGKAH_VOLUME, NAMA_APLIKASI, NAMA_LAGU_DISUKAI, VOLUME_AWAL,
)
from mymusic.core.favorit import favorit
from mymusic.core.pekerja import jalankan_di_latar
from mymusic.core.pemutar import Pemutar
from mymusic.services.daftar_tersimpan import DaftarTersimpan
from mymusic.services.penyimpanan import PenyimpananPlaylist
from mymusic.services.sesi import PenyimpananSesi
from mymusic.services.youtube import (
    adalah_link, ambil_album, ambil_artis, ambil_id_playlist, ambil_lirik, ambil_playlist, ambil_playlist_rekomendasi,
    ambil_rekomendasi_lagu, cari,
)
from mymusic.ui.bilah_atas import BilahAtas
from mymusic.ui.bilah_pemutar import BilahPemutar
from mymusic.ui.halaman_artis import HalamanArtis
from mymusic.ui.halaman_beranda import HalamanBeranda
from mymusic.ui.halaman_cari import HalamanCari
from mymusic.ui.halaman_lirik import HalamanLirik
from mymusic.ui.halaman_playlist import ALBUM, SAYA, SUKA, YOUTUBE, HalamanPlaylist
from mymusic.ui.navigasi import navigasi
from mymusic.ui.panel_kanan import DIPUTAR, PanelKanan
from mymusic.ui.panel_koleksi import PanelKoleksi
from mymusic.ui.widgets import SAMPUL_SUKA, PanelBulat, Toast


class JendelaUtama(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(NAMA_APLIKASI)
        self.resize(1280, 820)
        self.setMinimumSize(1080, 680)

        self.pemutar = Pemutar(self)
        self.penyimpanan = PenyimpananPlaylist()
        self.penyimpanan_sesi = PenyimpananSesi()
        self.riwayat = DaftarTersimpan(FILE_RIWAYAT, BATAS_RIWAYAT)
        self.hasil_cari = []
        self.kata_cari = ""
        self.isi_playlist = []  # lagu yang tampil di halaman playlist
        self._nomor_permintaan = 0  # untuk mengabaikan hasil cari/playlist yang sudah basi
        self._id_rekomendasi = None
        # Riwayat navigasi untuk tombol ← →, seperti browser: daftar "lokasi" + posisi yang sedang dibuka.
        self._jejak = [("beranda",)]
        self._posisi_jejak = 0

        self._buat_tampilan()
        self._sambungkan_sinyal()
        self._pasang_pintasan()
        self._segarkan_koleksi()
        self.beranda.tampilkan_riwayat(self.riwayat.semua())
        self._pulihkan_sesi()
        jalankan_di_latar(ambil_playlist_rekomendasi,
                          selesai=self.beranda.tampilkan_playlist_rekomendasi,
                          gagal=self.beranda.tampilkan_gagal_playlist)
        self._muat_mirip_suka()

    # ---------- tampilan ----------

    def _buat_tampilan(self):
        self.bilah_atas = BilahAtas()
        self.koleksi = PanelKoleksi()
        self.beranda = HalamanBeranda()
        self.halaman_cari = HalamanCari()
        self.halaman_playlist = HalamanPlaylist()
        self.halaman_lirik = HalamanLirik()
        self.halaman_artis = HalamanArtis()
        self.tumpukan = QStackedWidget()
        for halaman in (self.beranda, self.halaman_cari, self.halaman_playlist, self.halaman_lirik, self.halaman_artis):
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
        self.bilah_atas.beranda.connect(lambda: self._pergi(("beranda",)))
        self.bilah_atas.mundur.connect(self.mundur)
        self.bilah_atas.maju.connect(self.maju)

        n = navigasi()
        n.buka_artis.connect(self.buka_artis)
        n.putar_artis.connect(self.putar_artis)
        n.buka_album.connect(self.buka_album)
        n.putar_album.connect(self.putar_album)

        self.koleksi.buka.connect(self.buka_playlist_saya)
        self.koleksi.putar.connect(self.putar_playlist_saya)
        self.koleksi.simpan_antrean.connect(self.simpan_antrean)

        b = self.beranda
        b.buka_playlist_saya.connect(self.buka_playlist_saya)
        b.putar_playlist_saya.connect(self.putar_playlist_saya)
        b.buka_playlist_yt.connect(lambda info: self.buka_playlist_yt(info.id, info.judul))
        b.putar_playlist_yt.connect(lambda info: self.buka_playlist_yt(info.id, info.judul, putar=True))
        b.putar_lagu.connect(self.pemutar.putar_daftar)
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

        a = self.halaman_artis
        a.putar.connect(lambda i: self.pemutar.putar_daftar(list(a.artis.lagu), i, a.artis.nama))
        a.putar_jeda.connect(self.klik_putar_artis)
        a.acak.connect(lambda: self.pemutar.atur_acak(not self.pemutar.antrean.acak))
        a.tambah.connect(self.tambah_ke_antrean)
        a.sisipkan.connect(self.sisipkan_ke_antrean)

        self.panel_kanan.tutup.connect(lambda: self.tampilkan_panel(None))
        self.panel_kanan.simpan_antrean.connect(self.simpan_antrean)
        self.bilah_pemutar.panel_diminta.connect(self._alihkan_panel)
        self.bilah_pemutar.lirik_diminta.connect(self._alihkan_lirik)
        self.halaman_lirik.geser.connect(self.pemutar.geser_ke)
        self.pemutar.posisi_berubah.connect(self.halaman_lirik.atur_posisi)

        self.pemutar.lagu_berubah.connect(self._lagu_berubah)
        self.pemutar.mode_berubah.connect(self._mode_berubah)
        self.pemutar.status_berubah.connect(lambda _: self._segarkan_tombol_putar())
        self.pemutar.pesan.connect(lambda pesan: pesan.startswith("Gagal") and self.toast.tampilkan(pesan))
        favorit().berubah.connect(self._favorit_berubah)

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
            "Alt+Shift+B": lambda: p.antrean.sekarang and favorit().alihkan(p.antrean.sekarang),
            "Alt+Left": self.mundur,
            "Alt+Right": self.maju,
        }
        for tombol, aksi in pintasan.items():
            QShortcut(QKeySequence(tombol), self).activated.connect(aksi)
        QApplication.instance().installEventFilter(self)  # tombol samping mouse, lihat eventFilter()

    def eventFilter(self, objek, event):
        # Tombol samping mouse (Back/Forward) berfungsi di mana pun di dalam jendela, seperti di browser.
        if event.type() == QEvent.MouseButtonPress and event.button() in (Qt.BackButton, Qt.ForwardButton):
            (self.mundur if event.button() == Qt.BackButton else self.maju)()
            return True
        return super().eventFilter(objek, event)

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

    # ---------- navigasi (← →) ----------

    def _pergi(self, lokasi, **opsi):
        """Membuka lokasi baru & mencatatnya. Riwayat "maju" dibuang, sama seperti di browser."""
        if lokasi != self._jejak[self._posisi_jejak]:
            del self._jejak[self._posisi_jejak + 1:]
            self._jejak.append(lokasi)
            self._posisi_jejak += 1
        self._buka_lokasi(lokasi, **opsi)

    def mundur(self):
        if self._posisi_jejak > 0:
            self._posisi_jejak -= 1
            self._buka_lokasi(self._jejak[self._posisi_jejak])

    def maju(self):
        if self._posisi_jejak < len(self._jejak) - 1:
            self._posisi_jejak += 1
            self._buka_lokasi(self._jejak[self._posisi_jejak])

    def _buka_lokasi(self, lokasi, **opsi):
        """lokasi = (jenis, argumen...), mis. ("artis", id) atau ("cari", "tulus")."""
        jenis, *argumen = lokasi
        buka = {
            "beranda": lambda: self.tampilkan_halaman(self.beranda),
            "cari": self._buka_cari,
            "playlist_yt": self._buka_playlist_yt,
            "playlist_saya": self._buka_playlist_saya,
            "artis": self._buka_artis,
            "album": self._buka_album,
            "lirik": self._buka_lirik,
        }[jenis]
        buka(*argumen, **opsi)
        self.bilah_atas.atur_navigasi(self._posisi_jejak > 0, self._posisi_jejak < len(self._jejak) - 1)

    def _alihkan_lirik(self):
        """Tombol lirik: buka halaman lirik, atau kembali ke halaman sebelumnya bila sudah terbuka."""
        if self.tumpukan.currentWidget() is self.halaman_lirik:
            self.mundur()
        else:
            self._pergi(("lirik",))

    def _buka_lirik(self):
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
        self._pergi(("cari", teks))

    def _buka_cari(self, teks):
        self._nomor_permintaan += 1
        nomor = self._nomor_permintaan
        self.bilah_atas.kotak_cari.setText(teks)  # saat kembali (←) ke pencarian lama
        self.tampilkan_halaman(self.halaman_cari)
        self.halaman_cari.tampilkan_memuat(teks)
        jalankan_di_latar(cari, teks,
                          selesai=lambda hasil: self._hasil_cari_siap(nomor, teks, hasil),
                          gagal=lambda pesan: self.halaman_cari.tampilkan_pesan(f"Pencarian gagal: {pesan}"))

    def _hasil_cari_siap(self, nomor, kata, hasil):
        if nomor != self._nomor_permintaan:
            return
        self.hasil_cari = list(hasil.lagu)
        self.kata_cari = kata
        self.halaman_cari.tampilkan(kata, hasil, self.pemutar.antrean.sekarang)

    def buka_playlist_yt(self, id_playlist, judul_sementara, putar=False):
        self._pergi(("playlist_yt", id_playlist, judul_sementara), putar=putar)

    def _buka_playlist_yt(self, id_playlist, judul_sementara, putar=False):
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
        self._segarkan_tombol_putar()

    # ---------- artis & album ----------

    def buka_artis(self, id_artis):
        self._pergi(("artis", id_artis))

    def _buka_artis(self, id_artis):
        self._nomor_permintaan += 1
        nomor = self._nomor_permintaan
        self.tampilkan_halaman(self.halaman_artis)
        self.halaman_artis.tampilkan_memuat()
        jalankan_di_latar(ambil_artis, id_artis,
                          selesai=lambda artis: self._artis_siap(nomor, artis),
                          gagal=self.halaman_artis.tampilkan_gagal)

    def _artis_siap(self, nomor, artis):
        if nomor != self._nomor_permintaan:
            return
        self.halaman_artis.tampilkan(artis, self.pemutar.antrean.sekarang)
        self._segarkan_tombol_putar()

    def putar_artis(self, id_artis):
        """Tombol ▶ di kartu artis: putar lagu populernya tanpa pindah halaman (seperti Spotify)."""
        jalankan_di_latar(ambil_artis, id_artis,
                          selesai=lambda artis: self.pemutar.putar_daftar(list(artis.lagu), sumber=artis.nama),
                          gagal=lambda pesan: self.toast.tampilkan(f"Gagal memuat artis: {pesan}"))

    def klik_putar_artis(self):
        artis = self.halaman_artis.artis
        if artis and self.pemutar.sumber == artis.nama and self.pemutar.antrean.sekarang:
            self.pemutar.putar_jeda()
        elif artis and artis.lagu:
            self.pemutar.putar_daftar(list(artis.lagu), sumber=artis.nama)

    def buka_album(self, id_album):
        self._pergi(("album", id_album))

    def _buka_album(self, id_album):
        self._nomor_permintaan += 1
        nomor = self._nomor_permintaan
        self.tampilkan_halaman(self.halaman_playlist)
        self.halaman_playlist.tampilkan_memuat("Album", ALBUM)
        jalankan_di_latar(ambil_album, id_album,
                          selesai=lambda album: self._album_siap(nomor, album),
                          gagal=self.halaman_playlist.tampilkan_gagal)

    def _album_siap(self, nomor, album):
        if nomor != self._nomor_permintaan:
            return
        self.isi_playlist = list(album.lagu)
        self.halaman_playlist.tampilkan_album(album, self.pemutar.antrean.sekarang)
        self._segarkan_tombol_putar()

    def putar_album(self, id_album):
        """Tombol ▶ di kartu album: putar albumnya tanpa pindah halaman."""
        jalankan_di_latar(ambil_album, id_album,
                          selesai=lambda album: self.pemutar.putar_daftar(list(album.lagu), sumber=album.judul),
                          gagal=lambda pesan: self.toast.tampilkan(f"Gagal memuat album: {pesan}"))

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

    def _segarkan_tombol_putar(self):
        """Tombol putar besar di halaman playlist/artis menjadi ⏸ bila isinya yang sedang diputar."""
        main = self.pemutar.sedang_memutar()
        self.halaman_playlist.atur_main(main and self.pemutar.sumber == self.halaman_playlist.judul)
        artis = self.halaman_artis.artis
        self.halaman_artis.atur_main(main and artis is not None and self.pemutar.sumber == artis.nama)

    def _mode_berubah(self):
        acak = self.pemutar.antrean.acak
        self.halaman_playlist.atur_acak(acak)
        self.halaman_artis.atur_acak(acak)

    def _lagu_berubah(self, lagu):
        self.halaman_cari.tandai(lagu)
        self.halaman_playlist.tandai(lagu)
        self.halaman_artis.tandai(lagu)
        self._tandai_koleksi()
        self._segarkan_tombol_putar()
        self._muat_lirik()
        if lagu:
            self.riwayat.tambah(lagu)
            self.beranda.tampilkan_riwayat(self.riwayat.semua())
        if lagu and lagu.video_id != self._id_rekomendasi:
            self._id_rekomendasi = lagu.video_id
            jalankan_di_latar(ambil_rekomendasi_lagu, lagu.video_id,
                              selesai=lambda daftar: self._rekomendasi_siap(lagu, daftar))

    def _rekomendasi_siap(self, lagu, daftar):
        if lagu.video_id == self._id_rekomendasi:
            self.beranda.tampilkan_rekomendasi_lagu(lagu, daftar)

    # ---------- Lagu yang Disukai & rekomendasi dari favorit ----------

    def _favorit_berubah(self, lagu, disukai):
        self.toast.tampilkan("Ditambahkan ke Lagu yang Disukai" if disukai else "Dihapus dari Lagu yang Disukai")
        self._segarkan_koleksi()
        p = self.halaman_playlist
        if p.jenis == SUKA:  # halaman Lagu yang Disukai sedang ditampilkan: perbarui isinya
            gulir = p.verticalScrollBar().value()
            self._buka_playlist_saya(NAMA_LAGU_DISUKAI, pindah_halaman=False)
            p.verticalScrollBar().setValue(gulir)  # jangan melompat ke atas setiap kali ♥ diklik

    def _muat_mirip_suka(self):
        """Rak "Karena kamu menyukai …" dari satu lagu favorit acak, sekali saat aplikasi dibuka."""
        if not len(favorit()):
            return
        lagu = random.choice(favorit().semua())
        jalankan_di_latar(ambil_rekomendasi_lagu, lagu.video_id,
                          selesai=lambda daftar: self.beranda.tampilkan_mirip_suka(lagu, daftar))

    # ---------- Koleksi Kamu (playlist tersimpan) ----------

    def _segarkan_koleksi(self):
        semua = [(nama, self.penyimpanan.ambil(nama)) for nama in self.penyimpanan.semua_nama()]
        self.koleksi.atur_jumlah_suka(len(favorit()))
        self.koleksi.isi([(nama, f"Playlist · {len(lagu)} lagu", lagu[0].sampul if lagu else "")
                          for nama, lagu in semua])
        pintasan = [(nama, lagu[0].sampul if lagu else "") for nama, lagu in semua]
        if len(favorit()):
            pintasan.insert(0, (NAMA_LAGU_DISUKAI, SAMPUL_SUKA))
        self.beranda.isi_pintasan(pintasan)
        self._tandai_koleksi()

    def _tandai_koleksi(self):
        p = self.halaman_playlist
        terbuka = p.judul if self.tumpukan.currentWidget() is p and p.jenis in (SAYA, SUKA) else None
        diputar = self.pemutar.sumber if self.pemutar.antrean.sekarang else None
        self.koleksi.tandai(terbuka, diputar)

    def _ambil_playlist_saya(self, nama):
        """Isi playlist di Koleksi Kamu; "Lagu yang Disukai" diambil dari favorit."""
        return favorit().semua() if nama == NAMA_LAGU_DISUKAI else self.penyimpanan.ambil(nama)

    def buka_playlist_saya(self, nama):
        self._pergi(("playlist_saya", nama))

    def _buka_playlist_saya(self, nama, pindah_halaman=True):
        self._nomor_permintaan += 1  # batalkan playlist YouTube yang mungkin masih dimuat
        self.isi_playlist = self._ambil_playlist_saya(nama)
        jenis = SUKA if nama == NAMA_LAGU_DISUKAI else SAYA
        self.halaman_playlist.tampilkan(jenis, nama, self.isi_playlist, self.pemutar.antrean.sekarang)
        if pindah_halaman:
            self.tampilkan_halaman(self.halaman_playlist)
        self._segarkan_tombol_putar()

    def putar_playlist_saya(self, nama):
        daftar = self._ambil_playlist_saya(nama)
        if daftar:
            self.pemutar.putar_daftar(daftar, sumber=nama)

    def _tanya_timpa(self, nama):
        if nama == NAMA_LAGU_DISUKAI:
            self.toast.tampilkan(f"Nama “{nama}” sudah dipakai, pilih nama lain")
            return False
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
            self._pergi(("beranda",))
            self.toast.tampilkan("Playlist dihapus")
