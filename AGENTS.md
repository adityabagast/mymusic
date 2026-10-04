# AGENTS.md — Konteks Proyek untuk AI Agent

> Baca file ini sampai habis sebelum mengerjakan apa pun. Isinya cukup untuk memahami
> proyek tanpa menganalisis ulang semua file. **Perbarui bagian "Status saat ini" dan
> "Riwayat keputusan" setiap kali kamu menyelesaikan pekerjaan.**

## 1. Ringkasan

**MyMusic** — aplikasi desktop pemutar musik untuk Windows. Mencari dan memutar lagu dari
YouTube Music secara streaming (tidak mengunduh), dengan antrean dan playlist.

| | |
|---|---|
| Bahasa | Python 3.14 (venv di `.venv/`) |
| GUI | PySide6 6.11 (Qt 6) — `QtWidgets`, `QtMultimedia` (backend FFmpeg), `QtNetwork` |
| Pencarian / playlist | `ytmusicapi` 1.12 — tanpa login (`YTMusic()`) |
| URL audio | `yt-dlp` 2026.8 — `extract_info(download=False)`, format `bestaudio[ext=m4a]` |
| OS pengguna | Windows 11, shell PowerShell |
| Git | repo lokal, branch `main`, remote `origin` = https://github.com/adityabagast/mymusic (`.gitignore`: `.venv/`, `__pycache__/`, `data/`, `*.png`, `.vscode/`) |

## 2. Tentang pengguna — WAJIB dipatuhi

- Pengguna **sedang belajar** dan membangun proyek ini **bertahap** (tahap 1, 2, 3, ...).
- Berkomunikasi dalam **bahasa Indonesia** yang santai.
- **Jangan langsung mengubah atau membuat file `.py`** kecuali pengguna jelas memintanya.
  Sejak tahap 3, pengguna ingin **diberi instruksi + kode + lokasi yang harus diubah**, lalu
  menulisnya sendiri. Berikan instruksi **langsung di chat**, per langkah — **jangan membuat
  file panduan/dokumentasi `.md`** (pengguna sudah meminta file seperti itu dihapus).
  Satu-satunya file `.md` yang dipelihara adalah file ini. Kalau ragu, tanyakan dulu.
- Bila pengguna melaporkan error setelah menyalin kode dan berkata "langsung update saja", agent boleh
  memperbaiki berkasnya langsung (pernah terjadi: indentasi bertambah 4 spasi saat menempel di VS Code).
- Kode yang diberikan ke pengguna **harus sudah diuji** (tulis & jalankan di folder sementara
  di luar proyek), karena pengguna akan menyalinnya apa adanya.
- Jelaskan *kenapa*, bukan hanya *apa* — termasuk bug yang ditemukan saat pengujian.

## 3. Status saat ini

_Terakhir diperbarui: 2026-10-04_

| Tahap | Isi | Status |
|---|---|---|
| 1 | `tahap1_cari.py` — CLI pencarian lagu | ✅ selesai |
| 2 | `tahap2_gui.py` — GUI: cari, putar, ⏮▶⏭, slider, volume, sampul, lanjut otomatis | ✅ selesai, teruji |
| 3 | Restrukturisasi ke paket `mymusic/` + antrean + impor link playlist + playlist tersimpan | ✅ selesai, diterapkan pengguna & berjalan |
| 4 | Tampilan ala Spotify (lihat di bawah) — dibagi 3 bagian: A fondasi (tema, ikon, widget dasar, model+album, rekomendasi di services), B komponen & halaman (baris_lagu, kartu, halaman_beranda/cari/playlist), C rangka (panel_koleksi, panel_kanan, bilah_atas, bilah_pemutar, jendela_utama; hapus ui/daftar_lagu.py) | ✅ selesai — Bagian A diterapkan pengguna (diperbaiki agent), B & C diterapkan langsung oleh agent atas permintaan pengguna; berjalan & teruji di proyek |
| 5 | Kenyamanan memutar: acak, ulang (mati/semua/satu), pintasan keyboard, sesi diingat (volume, antrean, posisi, mode, panel), drag & drop antrean, coba ulang otomatis saat URL ditolak | ✅ selesai — diterapkan langsung oleh agent atas pilihan pengguna; 26 pemeriksaan GUI lolos di proyek |
| 6 | Lirik: tombol 🎤 di bilah pemutar → halaman lirik di tengah (latar warna sampul), lirik bersinkron disorot & digulir otomatis, klik baris = lompat, gulir manual menjeda 4 dtk | ✅ selesai — diterapkan langsung oleh agent atas permintaan pengguna; 15 pemeriksaan GUI lolos di proyek |
| 7 | Favorit & riwayat: ♥ di bilah pemutar, panel Sedang diputar, setiap baris lagu, menu ⋯, Alt+Shift+B; "Lagu yang Disukai" di atas Koleksi Kamu & ubin Beranda (sampul gradasi aksen); rak Beranda "Baru diputar" dan "Karena kamu menyukai …" (radio dari 1 favorit acak saat aplikasi dibuka) | ✅ selesai — diterapkan langsung oleh agent atas permintaan pengguna; 32 pemeriksaan GUI + uji data lolos di proyek |
| 8 | Jelajah: halaman artis (banner, populer, album, single, artis serupa) & album (pakai HalamanPlaylist jenis ALBUM); nama artis/album bisa diklik di mana saja (LabelTautan); Cari menampilkan hasil teratas artis/album + rak Artis & Album; tombol ← → + Alt+←/→ + tombol samping mouse; ▶ di kartu artis/album memutar tanpa pindah halaman | ✅ selesai — diterapkan langsung oleh agent atas permintaan pengguna; 34 pemeriksaan GUI + uji data (API asli) lolos di proyek, regresi tahap 6 & 7 lolos |

**Isi folder saat ini:** struktur pada bagian 4 sudah lengkap (`main.py`, `requirements.txt`, `arsip/`, `mymusic/`), plus `AGENTS.md`, `CLAUDE.md`, `.venv/`. Folder `data/` (playlist.json, sesi.json, favorit.json, riwayat.json) dibuat otomatis dan tidak ikut ke Git.

**Tahap 4 = tampilan (UI/UX), acuan: Spotify — sudah diimplementasikan.** Prototipe: https://claude.ai/artifact/LS5QnVACGUXDJdU6tkPsMB (privat milik pengguna).
Yang ditiru dari Spotify hanya POLA UX — nama, logo, font, dan warna hijau Spotify sengaja tidak dipakai.
Ringkasan: jendela 1440×900; bilah atas 64 px (logo, tombol Beranda bulat, kotak cari pil di tengah);
panel kiri "Koleksi Kamu" 300 px (daftar playlist + tombol + simpan antrean); tengah = halaman Beranda
(salam waktu, ubin pintasan, kartu "Playlist Saya", ajakan impor link) / Cari (Hasil teratas + 4 lagu +
"Lagu lainnya") / Playlist & impor link (header bergradasi dari warna sampul, judul 64 px, tombol putar
bulat 56 px, tabel # / Judul / Album / durasi / ⋯); panel kanan 340 px = "Sedang diputar" (sampul besar +
"Berikutnya dalam antrean") ATAU "Antrean"; bilah pemutar 80 px. Menu ⋯ dan klik kanan: Tambah ke antrean,
Putar berikutnya. Warna: latar #000000, panel #121212, hover #1F1F1F, terpilih #2A2A2A, teks #FFFFFF,
teks redup #A7A7A7, aksen default #F5B841 (opsi #FF7A59, #2DD4BF, #A78BFA; teks di atas aksen #111).
Font Plus Jakarta Sans. Model `Lagu` perlu field baru `album` (tersedia di ytmusicapi). Tombol acak/ulang
sudah diberi tempat tapi baru berfungsi di tahap 5.

Bila pengguna melaporkan error setelah menyalin kode: bandingkan file pengguna dengan kode yang
diberikan (salah ketik nama variabel pernah terjadi: `BATAS_HASIL` vs `BATAS_HASIL_CARI`), lalu
beri tahu baris yang harus diperbaiki — jangan menimpa kode pengguna tanpa izin.

## 4. Struktur proyek (setelah tahap 8)

```
main.py                       titik masuk: .venv\Scripts\python.exe main.py (memasang font + QSS)
requirements.txt
arsip/                        tahap1_cari.py, tahap2_gui.py (referensi; tidak diimpor)
data/                         playlist.json, sesi.json, favorit.json, riwayat.json — dibuat otomatis (di .gitignore)
mymusic/
├── config.py                 SEMUA konstanta: path (FILE_PLAYLIST/SESI/FAVORIT/RIWAYAT), batas (BATAS_RIWAYAT=50), NAMA_LAGU_DISUKAI, VOLUME_AWAL, LANGKAH_VOLUME,
│                             LANGKAH_GESER_MS, JEDA_IKUTI_LIRIK_MS, AKSEN, LEBAR_KOLEKSI/PANEL_KANAN, OPSI_YTDLP
├── models.py                 Lagu(video_id, judul, artis, album, durasi, sampul, daftar_artis=((nama,id),...), id_album)
│                             + .teks .detik; InfoPlaylist; InfoArtis; InfoAlbum; Artis; Album; HasilCari;
│                             Lirik(baris, waktu ms, sumber) + .bersinkron .indeks_pada(ms) (bisect)
├── aset/font/                Plus Jakarta Sans *.ttf (dimuat ui/tema.muat_font, cadangan Segoe UI)
├── services/                 TANPA Qt
│   ├── youtube.py            cari (HasilCari, @lru_cache), ambil_artis, ambil_album (@lru_cache), cari_lagu, ambil_playlist, ambil_rekomendasi_lagu (radio), ambil_playlist_rekomendasi
│   │                         (get_home), ambil_lirik (get_watch_playlist → id lirik → get_lyrics timestamps=True; None bila tak ada),
│   │                         perbesar_sampul, ambil_url_audio, adalah_link, ambil_id_playlist
│   ├── penyimpanan.py        PenyimpananPlaylist (JSON {"nama": [lagu,...]})
│   ├── daftar_tersimpan.py   DaftarTersimpan(path, batas): JSON [lagu,...] terbaru di depan, tanpa dobel;
│   │                         semua/ada/tambah/hapus — dipakai favorit & riwayat
│   └── sesi.py               PenyimpananSesi: data/sesi.json {volume, panel, pemutar: {...}}; rusak/hilang -> {}
├── core/
│   ├── favorit.py            Favorit(QObject) + favorit() (satu objek, seperti pemuat_sampul); sinyal
│   │                         berubah(lagu, disukai); ada/alihkan/semua — SATU sumber data untuk semua tombol ♥
│   ├── antrean.py            Antrean (Python murni): lagu[], indeks, acak, ulang (ULANG_MATI/SEMUA/SATU),
│   │                         tambah/hapus/pindahkan/berikutnya, atur_acak (urutan asli dikembalikan), ke_dict/muat_dict
│   ├── pekerja.py            Pekerja(QRunnable) + jalankan_di_latar(fungsi, *args, selesai=, gagal=)
│   ├── pemutar.py            Pemutar(QObject) = QMediaPlayer + Antrean; .sumber, sedang_memutar(), atur_acak,
│   │                         ganti_mode_ulang, pindahkan, geser_relatif, ke_sesi/pulihkan_sesi, coba ulang 1x saat error
│   └── sampul.py             pemuat_sampul(): unduh gambar sekali + cache di memori
└── ui/
    ├── tema.py               warna (LATAR, PANEL, HOVER, ...), muat_font(), stylesheet(font) — QSS memakai
    │                         properti `peran` (label) dan `jenis` (tombol), plus objectName (#baris, #kartu, ...)
    ├── ikon.py               ikon SVG garis (dict _IKON) → ikon()/pixmap_ikon() via QSvgRenderer
    ├── widgets.py            LabelPotong, LabelTautan (nama artis/album yang bisa diklik → navigasi()), tautan_artis,
    │                         TombolIkon, TombolSuka (♥ yang ikut favorit().berubah), TombolBulat,
    │                         Sampul (+ SAMPUL_SUKA → gambar_sampul_suka, atur_sudut), LatarGradasi, PanelBulat, Toast,
    │                         atur_properti, label, warna_dominan, campur_warna, kosongkan_tata
    ├── baris_lagu.py         BarisLagu (# / sampul+judul / album / ♥ / durasi / ⋯, mode ringkas), KepalaTabel,
    │                         DaftarLagu(isi, tandai), tampilkan_menu_lagu(induk, posisi, lagu, tambah, sisipkan)
    ├── kartu.py              Kartu(bulat=), Ubin, RakKartu (sembunyikan kartu yang tak muat), KartuTeratas.atur(judul, ket,
    │                         sampul, bulat), BagianKartu, kartu_album/kartu_artis (klik → navigasi())
    ├── navigasi.py           Navigasi + navigasi(): sinyal buka_artis/putar_artis/buka_album/putar_album (satu objek)
    ├── halaman_beranda.py    salam, ubin Koleksi, BagianLagu: "Baru diputar" / "Karena kamu memutar …" /
    │                         "Karena kamu menyukai …" (sinyal putar_lagu(daftar, i, sumber)), "Playlist rekomendasi", ajakan link
    ├── halaman_cari.py       Hasil teratas (artis/album/lagu) + 4 lagu (ringkas) + rak Artis & Album + Lagu lainnya
    ├── halaman_playlist.py   header bergradasi dari warna sampul, tombol aksi, tabel; jenis SAYA / YOUTUBE / SUKA / ALBUM
    │                         (tampilkan_album: nama artis = tautan rich text → linkActivated; kolom Album disembunyikan)
    ├── halaman_artis.py      HalamanArtis: KepalaArtis (banner cover-fit + nama), putar/acak, Populer, rak album/single/serupa
    ├── halaman_lirik.py      HalamanLirik (QScrollArea, latar dilukis di viewport), BarisLirik; properti QSS
    │                         `keadaan` = lewat/aktif/nanti/biasa; sinyal geser(ms); .video_id = lagu yang ditampilkan
    ├── panel_koleksi.py      panel kiri "Koleksi Kamu": item_suka tetap di atas + ItemKoleksi playlist (terpilih & diputar)
    ├── panel_kanan.py        "Sedang diputar" (+ ♥) / "Antrean" (BarisAntrean, DaftarGeser = drag & drop urutan)
    ├── bilah_atas.py         logo, tombol ← → (atur_navigasi), tombol Beranda, kotak cari (Enter → sinyal cari)
    ├── bilah_pemutar.py      3 kolom: lagu + ♥ (menempel di belakang judul) | kendali + progres | tombol panel, lirik (🎤) + volume
    └── jendela_utama.py      merangkai semuanya + navigasi, cari, link, antrean, Koleksi, rekomendasi, lirik (_alihkan_lirik/_muat_lirik),
                              favorit (_favorit_berubah, _muat_mirip_suka), riwayat (self.riwayat, dicatat di _lagu_berubah),
                              artis & album (buka_/putar_), riwayat navigasi ← → (_jejak, _pergi, _buka_lokasi, mundur/maju;
                              semua pindah halaman lewat _pergi), pintasan (_pasang_pintasan + eventFilter tombol mouse),
                              sesi (_pulihkan_sesi / closeEvent)
```

Pintasan: Spasi putar/jeda · Ctrl+→/← berikutnya/sebelumnya · Shift+→/← geser 5 detik · Ctrl+↑/↓ volume ·
Ctrl+F kotak cari · Ctrl+S acak · Ctrl+R mode ulang · Alt+Shift+B suka/batal suka lagu yang diputar · Alt+←/→ (dan tombol samping mouse) kembali/maju (meniru Spotify desktop).

Signal milik `Pemutar`: `lagu_berubah(object)`, `antrean_berubah()`, `mode_berubah()`, `status_berubah(bool)`,
`posisi_berubah(int)`, `durasi_berubah(int)`, `pesan(str)`. Tampilan tidak memakai status bar lagi:
pesan yang diawali "Gagal" ditampilkan sebagai toast.

Daftar lagu sengaja memakai widget baris di dalam QScrollArea (bukan QTableView) agar header halaman dan
tabel bergulir bersama seperti Spotify. Untuk daftar sangat panjang (ribuan lagu) ini perlu dioptimasi.

## 5. Aturan arsitektur

1. **Impor hanya satu arah:** `ui → core → services → models/config`. Tidak boleh sebaliknya.
2. `services/` **tidak boleh mengimpor Qt**. Fungsi di sana mengembalikan `Lagu` / `list[Lagu]`,
   bukan dict mentah ytmusicapi.
3. `core/` tidak boleh mengimpor `ui/`. Komunikasi ke tampilan **lewat Signal**.
4. Data hanya punya satu pemilik: antrean ada di `Antrean`; widget menggambar ulang dari data
   (`DaftarLagu.isi()`) saat ada Signal — jangan menyimpan state di widget.
5. Konstanta baru → `config.py`. Fitur baru → file baru di lapisan yang sesuai
   (lihat tabel di bagian 10).
6. Semua pemanggilan jaringan (ytmusicapi, yt-dlp) **wajib** lewat `jalankan_di_latar()`,
   tidak pernah langsung di thread GUI.

## 6. Konvensi kode

- Nama variabel, fungsi, kelas, komentar, docstring, dan teks UI: **bahasa Indonesia**
  (`cari_lagu`, `JendelaUtama`, `daftar_lagu`, `"Menyiapkan audio..."`). API Qt/library tetap aslinya.
- Gaya mengikuti kode yang ada: docstring singkat satu baris, komentar hanya untuk hal yang
  tidak jelas, metode dikelompokkan dengan `# ---------- judul ----------`.
- Metode internal diawali `_`. Pembuatan widget di `_buat_tampilan()`, koneksi sinyal di
  `_sambungkan_sinyal()`.
- Tanpa dependensi baru kecuali benar-benar perlu; bila ditambah, catat di `requirements.txt`.

## 7. Jebakan yang sudah diketahui (jangan diulang)

| Masalah | Penyebab | Solusi yang dipakai |
|---|---|---|
| Callback `jalankan_di_latar` tidak pernah terpanggil | PySide hanya memegang referensi **lemah** ke fungsi lokal, sehingga dibuang GC | `_pekerja_aktif` (set) di `pekerja.py` menyimpan pekerja sampai selesai; callback dibungkus lambda |
| `RuntimeError: Failed to connect signal positionChanged(qlonglong)` | Signal→Signal harus bertipe sama (`qint64` vs `int`) | sambungkan ke `self.posisi_berubah.emit` |
| `QLabel(fixedSize=...)`, `QSlider(fixedWidth=...)` error | Bukan Q_PROPERTY, tak bisa jadi kwarg | panggil `setFixedSize()` / `setFixedWidth()` |
| Mix (`list=RD...`) gagal dengan `get_playlist` | Mix bukan playlist sungguhan | `get_watch_playlist(playlistId=...)` |
| Data Mix pakai `length` & `thumbnail` | Beda kunci dengan search/playlist (`duration`, `thumbnails`) | ditangani di `Lagu.dari_ytmusic()` |
| Lagu tidak bisa diputar ulang setelah beberapa jam | URL googlevideo kedaluwarsa (~6 jam) | **jangan simpan URL audio**; panggil `ambil_url_audio()` setiap kali memutar |
| Peringatan yt-dlp "No supported JavaScript runtime" | deno tidak terpasang | audio m4a tetap jalan; disembunyikan via `no_warnings`. Bila lagu mulai gagal diputar → sarankan pasang deno |
| `UnicodeEncodeError` saat `print()` judul ber-emoji | Konsol Windows cp1252 | `PYTHONIOENCODING=utf-8` saat tes, atau `sys.stdout.reconfigure(encoding="utf-8")` |
| `ytmusicapi.search(limit=...)` mengembalikan lebih banyak | perilaku library (mis. 20–30 hasil) | tidak masalah, jangan diandalkan |
| Log FFmpeg muncul di terminal saat memutar | backend FFmpeg Qt | tidak berbahaya, abaikan |
| Pintasan keyboard tidak bereaksi saat diuji | QShortcut hanya aktif bila jendela sedang aktif (fokus) | wajar; dalam uji otomatis picu `QShortcut.activated.emit()` |
| Uji GUI gagal "tanpa lagu" pada percobaan kedua | `closeEvent` menyimpan sesi, jadi run berikutnya memulihkan lagu | hapus `data/` di folder uji; saat menguji kode di proyek, arahkan `PenyimpananSesi.__init__.__defaults__` ke file sementara agar sesi pengguna tidak tertimpa |
| Kolom kepala tabel bergeser 16 px dari kolom baris lagu (sejak tahap 4) | QBoxLayout tidak memberi `setSpacing` di samping spacer (`addSpacing`) | kolom tombol di `KepalaTabel` diisi `_tempat_kosong(lebar)` (QWidget kosong), bukan `addSpacing` |
| Label dalam QVBoxLayout terpotong lebih pendek dari teksnya | lebar maksimum layout = batas TERKECIL dari isinya | beri `setMaximumWidth` yang sama (yang terlebar) ke semua label di kolom itu |
| Stretch di belakang widget "mencuri" separuh ruang | stretch factor sama-sama 1 dibagi rata | `addStretch()` (stretch 0) hanya mengambil sisa ruang yang tidak dipakai |
| Uji menu ⋯ menggantung: langkah uji berikutnya berjalan di dalam `menu.exec()` | `QAction.trigger()` tidak menutup QMenu | dalam uji: `menu.setActiveAction(aksi)` lalu `QTest.keyClick(menu, Qt.Key_Return)` |
| Uji tahap 7 menyentuh data pengguna | favorit/riwayat/sesi/playlist punya path bawaan di `data/` | sebelum impor modul lain: ubah `mymusic.config.FILE_*` ke folder sementara (lihat skrip uji tahap 7) |
| `Lagu.dari_ytmusic` crash untuk lagu dari `get_album` | di sana `album` berupa teks (nama), bukan dict; `thumbnails` = None | `isinstance(album, str)`; `Album.dari_ytmusic` mengisi sampul/id album dari albumnya |
| Lagu populer di `get_artist` tanpa durasi | ytmusicapi tidak menyertakannya | durasi "?" ditampilkan kosong di BarisLagu |
| Hasil teratas artis tidak punya `browseId` | bentuk data "Top result" berbeda | id & nama diambil dari `artists[0]` (InfoArtis.dari_ytmusic) |
| `QTest.mouseMove` tidak memicu `mouseMoveEvent` (uji sorot) | di Windows hanya memindahkan kursor | kirim `QMouseEvent(QEvent.MouseMove, ...)` dengan `QApplication.sendEvent` |
| Uji lama gagal "kembali ke halaman sebelumnya" | `tampilkan_halaman()` langsung tidak tercatat di riwayat ← → | di uji & kode, pindah halaman lewat `_pergi()` / `mulai_cari()` / `buka_*()` |
| Uji GUI berhenti setelah `jendela.close()` | Qt keluar saat jendela terakhir ditutup | `app.setQuitOnLastWindowClosed(False)` di skrip uji |
| Baris lama sempat terlihat bertumpuk setelah daftar diisi ulang | widget yang di-`deleteLater()` masih tampil sampai event loop berjalan | `kosongkan_tata` memanggil `hide()` dulu |
| `HTTP error 403 Forbidden` sesekali dari googlevideo | YouTube menolak sementara (terlihat setelah banyak permintaan beruntun) | Pemutar meminta URL baru sekali & lanjut dari posisi yang sama; pesan "Gagal memutar" baru muncul bila gagal lagi |
| `setSource()` dengan URL yang sama persis tidak memuat ulang | QMediaPlayer mengabaikan sumber yang tidak berubah | yt-dlp selalu memberi URL baru; dalam uji gunakan URL palsu yang berbeda-beda |
| `setPosition()` diabaikan tepat setelah `setSource()` | lagu belum dimuat | simpan di `_posisi_tunda`, terapkan saat status LoadedMedia/BufferedMedia |
| Playlist privat / ID ngawur → error teknis panjang | ytmusicapi melempar error parsing | dibungkus `RuntimeError("Playlist tidak ditemukan atau bersifat privat.")` |

## 8. Perintah

```powershell
# menjalankan (tahap 3)
.venv\Scripts\python.exe main.py
# menjalankan tahap 2 (sebelum dipindah ke arsip/)
.venv\Scripts\python.exe tahap2_gui.py
# pasang ulang dependensi
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Bash (Git Bash) juga tersedia: gunakan `.venv/Scripts/python.exe`.

## 9. Cara menguji tanpa interaksi manusia

Tidak ada test suite. Pola yang dipakai dan terbukti jalan:

- **Logika murni** (`Antrean`, `Lagu`, `ambil_id_playlist`): skrip Python biasa dengan `assert`.
- **GUI**: buat `QApplication` + `JendelaUtama`, set volume 0, jalankan langkah berurutan dengan
  `QTimer.singleShot(ms, fungsi)` (cari → `daftar_hasil.itemActivated.emit(item)` → tunggu ~10 dtk →
  cek `pemutar._player.playbackState()` / `position()`), simpan tangkapan layar dengan
  `jendela.grab().save("x.png")`, lalu `app.quit()`. Butuh internet.
- Kerjakan pengujian di folder sementara, **bukan** di folder proyek pengguna (lihat bagian 2).

Contoh link uji: playlist publik `https://www.youtube.com/playlist?list=PL9y1tLe074BDmrM7DO1nBfu6265mRJ6DF`
(121 lagu), Mix `https://music.youtube.com/watch?v=YKK5_OQiEa4&list=RDAMVMYKK5_OQiEa4`.

## 10. Rencana tahap berikutnya (belum dikerjakan)

Disepakati dengan pengguna (2026-10-04): **.exe dibuat di tahap 10, sebagai tahap terakhir** fitur inti.

| Tahap | Isi | Catatan |
|---|---|---|
| 9 | Ikon tray + tombol media keyboard (Play/Next/Prev) + kontrol di overlay media Windows; ikon aplikasi (.ico) | perilaku khas Windows ini sebaiknya ada sebelum dibungkus .exe |
| 10 | Jadi .exe (PyInstaller) + cara memperbarui yt-dlp | yt-dlp ikut "terkunci" di dalam .exe → perlu jalan keluar saat YouTube berubah (mis. build ulang, atau yt-dlp diperbarui terpisah) |
| nanti | Unduh untuk offline (`services/unduhan.py`, yt-dlp `download=True`) · tema terang & pilihan aksen (`ui/tema.py`) · "Tampilkan semua" lagu artis (browseId `songs` → playlist) | bisa sebelum/sesudah .exe |

## 11. Riwayat keputusan

- **2026-10-02** — Tahap 2: streaming via `QMediaPlayer` langsung dari URL yt-dlp (tanpa unduh);
  pekerjaan jaringan di `QThreadPool`; `nomor_permintaan` untuk mengabaikan hasil basi.
- **2026-10-02** — Tahap 3 dirancang: pecah ke paket berlapis; pisahkan "hasil" vs "antrean";
  klik dua kali di Hasil = ganti antrean dengan semua hasil (gaya Spotify); playlist disimpan
  sebagai JSON tanpa URL audio. Pengguna meminta instruksi + kode, bukan agent yang menulis file.
- **2026-10-02** — Pengguna meminta file panduan di `docs/` dihapus; instruksi tahap 3 diberikan di chat.
  Mulai sekarang instruksi selalu di chat; `AGENTS.md` satu-satunya dokumen.
- **2026-10-02** — Tahap 3 diterapkan pengguna dan berjalan (satu salah ketik di `config.py` diperbaiki).
- **2026-10-02** — Tahap 4 dimulai: pengguna minta prototipe UI/UX dulu sebelum implementasi; prototipe dibuat sebagai artifact desain (lihat bagian 3).
- **2026-10-02** — Pengguna memilih Spotify sebagai acuan; prototipe direvisi ke pola 3 panel ala Spotify dengan identitas sendiri.
- **2026-10-02** — Implementasi tahap 4 selesai diuji agent (get_home bisa tanpa login → rak "Playlist rekomendasi"; radio get_watch_playlist → "Karena kamu memutar"). Keputusan: daftar lagu memakai widget baris (QFrame) dalam QScrollArea, bukan QTableView, agar header & tabel bergulir bersama seperti Spotify; ikon SVG digambar via QSvgRenderer; `Lagu.teks` dipertahankan (dipakai tooltip & agar UI tahap 3 tetap jalan setelah Bagian A). Pekerja kini menelan `RuntimeError` saat emit setelah jendela ditutup.
- **2026-10-02** — Bagian A tahap 4 diterapkan; agent memperbaiki langsung atas permintaan pengguna: indentasi `def run`/`def sedang_memutar`, baris `antrean_berubah.emit()` yang terhapus di `putar_daftar`, dan `ui/ikon.py` yang belum dibuat.
- **2026-10-02** — Pengguna minta Bagian B & C langsung diterapkan; agent menyalin berkas teruji, menghapus `ui/daftar_lagu.py`, dan menguji di proyek (cari, putar, menu, panel, link playlist, rekomendasi). Tahap 4 selesai. Tombol acak/ulang masih nonaktif (tahap 5).
- **2026-10-02** — Tahap 5 selesai. Keputusan: acak memindahkan lagu yang diputar ke depan lalu mengacak sisanya (urutan asli disimpan di `_asli` dan dikembalikan saat acak dimatikan); "Putar" tanpa posisi saat acak aktif mulai dari lagu acak; ulang satu ditangani Pemutar saat EndOfMedia (tombol ⏭ tetap pindah lagu); sesi disimpan di `closeEvent` dan dipulihkan tanpa langsung memutar (tombol putar melanjutkan dari posisi terakhir); pintasan meniru Spotify desktop. Pengguna memilih agar agent menerapkan langsung.
- **2026-10-04** — Proyek dimasukkan ke Git oleh pengguna (dipandu di chat) dan di-push ke GitHub; commit awal `824580c`.
- **2026-10-04** — Tahap 6 (lirik) selesai. Keputusan: lirik tampil sebagai halaman di tengah (seperti Spotify), bukan mode panel kanan; hanya diambil saat halaman lirik terbuka (hemat permintaan, kurangi risiko 403) dan tidak diambil ulang untuk lagu yang sama; `Lirik` menyeragamkan dua bentuk hasil `get_lyrics` (list LyricLine vs string). Catatan: timestamp lirik dibuat untuk versi audio, jadi bisa meleset di video klip. Pengguna minta agent menerapkan langsung.
- **2026-10-04** — Tahap 7 (favorit & riwayat) selesai. Keputusan: `Favorit` di core sebagai satu objek global `favorit()` (pola `pemuat_sampul()`) agar setiap `TombolSuka` bisa membaca & mendengarkan tanpa diteruskan lewat banyak konstruktor; sinyal `berubah(lagu, disukai)` membuat setiap tombol hanya memperbarui dirinya bila video_id cocok. Favorit & riwayat memakai satu kelas `DaftarTersimpan` (riwayat dibatasi 50, dicatat setiap `lagu_berubah`). "Lagu yang Disukai" diperlakukan sebagai playlist berjenis SUKA dengan nama khusus (`NAMA_LAGU_DISUKAI`, ditolak sebagai nama playlist baru) dan sampul `SAMPUL_SUKA` agar pola (nama, keterangan, url) di Koleksi/Beranda tetap sama. Rak Beranda dijadikan `BagianLagu` + satu sinyal `putar_lagu(daftar, i, sumber)` (menggantikan `putar_rekomendasi`). Sekalian memperbaiki kolom kepala tabel yang bergeser sejak tahap 4.
- **2026-10-04** — Tahap 8 (artis & album) selesai. Keputusan: `Lagu` mendapat `daftar_artis` ((nama, id), ...) & `id_album` (data lama tetap terbaca, tampil sebagai teks biasa); nama artis/album jadi tautan lewat `LabelTautan` yang menggambar & memotong teksnya sendiri; perpindahan halaman dari widget mana pun lewat satu objek `navigasi()` (pola `favorit()`); riwayat ← → berupa daftar "lokasi" (tuple) dan SEMUA perpindahan halaman lewat `_pergi()`; `cari`/`ambil_artis`/`ambil_album` memakai `lru_cache` (aman karena dataclass frozen berisi tuple) agar ← → instan; ▶ di kartu artis/album memutar tanpa pindah halaman (seperti Spotify); halaman album memakai ulang HalamanPlaylist. Rencana: tahap 9 tray + tombol media, tahap 10 .exe.
