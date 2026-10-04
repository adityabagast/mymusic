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
| Git | belum dipakai (bukan repository) |

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

_Terakhir diperbarui: 2026-10-02_

| Tahap | Isi | Status |
|---|---|---|
| 1 | `tahap1_cari.py` — CLI pencarian lagu | ✅ selesai |
| 2 | `tahap2_gui.py` — GUI: cari, putar, ⏮▶⏭, slider, volume, sampul, lanjut otomatis | ✅ selesai, teruji |
| 3 | Restrukturisasi ke paket `mymusic/` + antrean + impor link playlist + playlist tersimpan | ✅ selesai, diterapkan pengguna & berjalan |
| 4 | Tampilan ala Spotify (lihat di bawah) — dibagi 3 bagian: A fondasi (tema, ikon, widget dasar, model+album, rekomendasi di services), B komponen & halaman (baris_lagu, kartu, halaman_beranda/cari/playlist), C rangka (panel_koleksi, panel_kanan, bilah_atas, bilah_pemutar, jendela_utama; hapus ui/daftar_lagu.py) | ✅ selesai — Bagian A diterapkan pengguna (diperbaiki agent), B & C diterapkan langsung oleh agent atas permintaan pengguna; berjalan & teruji di proyek |
| 5 | Kenyamanan memutar: acak, ulang (mati/semua/satu), pintasan keyboard, sesi diingat (volume, antrean, posisi, mode, panel), drag & drop antrean, coba ulang otomatis saat URL ditolak | ✅ selesai — diterapkan langsung oleh agent atas pilihan pengguna; 26 pemeriksaan GUI lolos di proyek |

**Isi folder saat ini:** struktur pada bagian 4 sudah lengkap (`main.py`, `requirements.txt`, `arsip/`, `mymusic/`), plus `AGENTS.md`, `CLAUDE.md`, `.venv/`. Folder `data/` muncul setelah playlist pertama disimpan.

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

## 4. Struktur proyek (setelah tahap 4)

```
main.py                       titik masuk: .venv\Scripts\python.exe main.py (memasang font + QSS)
requirements.txt
arsip/                        tahap1_cari.py, tahap2_gui.py (referensi; tidak diimpor)
data/playlist.json            dibuat otomatis saat playlist pertama disimpan
mymusic/
├── config.py                 SEMUA konstanta: path (FILE_PLAYLIST, FILE_SESI), batas, VOLUME_AWAL, LANGKAH_VOLUME,
│                             LANGKAH_GESER_MS, AKSEN, LEBAR_KOLEKSI/PANEL_KANAN, OPSI_YTDLP
├── models.py                 Lagu(video_id, judul, artis, album="", durasi, sampul) + .teks .detik; InfoPlaylist
├── aset/font/                Plus Jakarta Sans *.ttf (dimuat ui/tema.muat_font, cadangan Segoe UI)
├── services/                 TANPA Qt
│   ├── youtube.py            cari_lagu, ambil_playlist, ambil_rekomendasi_lagu (radio), ambil_playlist_rekomendasi
│   │                         (get_home), perbesar_sampul, ambil_url_audio, adalah_link, ambil_id_playlist
│   ├── penyimpanan.py        PenyimpananPlaylist (JSON {"nama": [lagu,...]})
│   └── sesi.py               PenyimpananSesi: data/sesi.json {volume, panel, pemutar: {...}}; rusak/hilang -> {}
├── core/
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
    ├── widgets.py            LabelPotong, TombolIkon, TombolBulat, Sampul, LatarGradasi, PanelBulat, Toast,
    │                         atur_properti, label, warna_dominan, campur_warna, kosongkan_tata
    ├── baris_lagu.py         BarisLagu (# / sampul+judul / album / durasi / ⋯, mode ringkas), KepalaTabel,
    │                         DaftarLagu(isi, tandai), tampilkan_menu_lagu (QMenu Tambah ke antrean/Putar berikutnya)
    ├── kartu.py              Kartu, Ubin, RakKartu (sembunyikan kartu yang tak muat), KartuTeratas
    ├── halaman_beranda.py    salam, ubin Koleksi, "Karena kamu memutar …", "Playlist rekomendasi", ajakan link
    ├── halaman_cari.py       Hasil teratas + 4 lagu (ringkas) + Lagu lainnya
    ├── halaman_playlist.py   header bergradasi dari warna sampul, tombol aksi, tabel; jenis SAYA / YOUTUBE
    ├── panel_koleksi.py      panel kiri "Koleksi Kamu" (ItemKoleksi, tanda terpilih & sedang diputar)
    ├── panel_kanan.py        "Sedang diputar" / "Antrean" (BarisAntrean, DaftarGeser = drag & drop urutan)
    ├── bilah_atas.py         logo, tombol Beranda, kotak cari (Enter → sinyal cari)
    ├── bilah_pemutar.py      3 kolom: lagu | kendali + progres | tombol panel + volume
    └── jendela_utama.py      merangkai semuanya + navigasi, cari, link, antrean, Koleksi, rekomendasi,
                              pintasan keyboard (_pasang_pintasan), sesi (_pulihkan_sesi / closeEvent)
```

Pintasan: Spasi putar/jeda · Ctrl+→/← berikutnya/sebelumnya · Shift+→/← geser 5 detik · Ctrl+↑/↓ volume ·
Ctrl+F kotak cari · Ctrl+S acak · Ctrl+R mode ulang (meniru Spotify desktop).

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

## 10. Ide tahap berikutnya (belum dikerjakan)

Unduh untuk offline · lirik (`get_lyrics`) · halaman artis/album · cari album/artis · favorit & riwayat ·
jadi .exe (PyInstaller) + ikon tray + tombol media keyboard Windows · tema terang.

| Fitur | File yang diubah / dibuat |
|---|---|
| Unduh untuk offline | `services/unduhan.py` (baru, yt-dlp `download=True`), tombol di tab Hasil |
| Tema | `ui/tema.py` (baru, stylesheet), dipasang di `main.py` |
| Lirik | fungsi baru di `services/youtube.py` (`get_watch_playlist` → `lyrics` id → `get_lyrics`), panel baru di `ui/` |
| Cari album/artis | parameter `filter=` di `services/youtube.py`, pilihan di `ui/jendela_utama.py` |

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
