"""Semua pengaturan aplikasi dikumpulkan di sini supaya mudah diubah."""
import os
from pathlib import Path

NAMA_APLIKASI = "MyMusic"
ID_APLIKASI = "MyMusic.PemutarMusik"  # AppUserModelID Windows: agar taskbar memakai ikon kita, bukan ikon Python
NAMA_LAGU_DISUKAI = "Lagu yang Disukai"

# Data pengguna di %LOCALAPPDATA%\MyMusic: tidak ikut terhapus saat .exe dibangun ulang, dan sama untuk main.py & .exe.
FOLDER_DATA = Path(os.environ.get("LOCALAPPDATA", Path.home())) / NAMA_APLIKASI
FILE_PLAYLIST = FOLDER_DATA / "playlist.json"
FILE_SESI = FOLDER_DATA / "sesi.json"
FILE_FAVORIT = FOLDER_DATA / "favorit.json"
FILE_RIWAYAT = FOLDER_DATA / "riwayat.json"
FOLDER_YTDLP = FOLDER_DATA / "yt-dlp"  # hasil "Perbarui yt-dlp", satu folder per versi
FOLDER_FONT = Path(__file__).resolve().parent / "aset" / "font"
FILE_IKON = Path(__file__).resolve().parent / "aset" / "ikon.ico"  # dibuat oleh alat/buat_ikon.py

BATAS_HASIL_CARI = 20
BATAS_LAGU_MIX = 50
BATAS_REKOMENDASI = 8  # jumlah kartu per rak di Beranda
BATAS_RIWAYAT = 50  # lagu yang diingat di riwayat "Baru diputar"
VOLUME_AWAL = 70  # 0 - 100
LANGKAH_VOLUME = 10  # Ctrl+↑ / Ctrl+↓
LANGKAH_GESER_MS = 5000  # Shift+→ / Shift+←
JEDA_IKUTI_LIRIK_MS = 4000  # setelah lirik digulir manual, berhenti mengikuti lagu selama ini

# Tampilan
AKSEN = "#CDBBFF"  # lavender pastel, senada dengan ikon (sebelumnya kuning #F5B841)
LEBAR_KOLEKSI = 280
LEBAR_PANEL_KANAN = 320

OPSI_YTDLP = {
    "format": "bestaudio[ext=m4a]/bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
}
URL_PYPI_YTDLP = "https://pypi.org/pypi/yt-dlp/json"  # sumber versi terbaru untuk "Perbarui yt-dlp"