"""Semua pengaturan aplikasi dikumpulkan di sini supaya mudah diubah."""
from pathlib import Path

NAMA_APLIKASI = "MyMusic"

FOLDER_PROYEK = Path(__file__).resolve().parent.parent
FOLDER_DATA = FOLDER_PROYEK / "data"
FILE_PLAYLIST = FOLDER_DATA / "playlist.json"
FILE_SESI = FOLDER_DATA / "sesi.json"
FOLDER_FONT = Path(__file__).resolve().parent / "aset" / "font"

BATAS_HASIL_CARI = 20
BATAS_LAGU_MIX = 50
BATAS_REKOMENDASI = 8  # jumlah kartu per rak di Beranda
VOLUME_AWAL = 70  # 0 - 100
LANGKAH_VOLUME = 10  # Ctrl+↑ / Ctrl+↓
LANGKAH_GESER_MS = 5000  # Shift+→ / Shift+←
JEDA_IKUTI_LIRIK_MS = 4000  # setelah lirik digulir manual, berhenti mengikuti lagu selama ini

# Tampilan
AKSEN = "#F5B841"  # pilihan lain dari prototipe: #FF7A59, #2DD4BF, #A78BFA
LEBAR_KOLEKSI = 280
LEBAR_PANEL_KANAN = 320

OPSI_YTDLP = {
    "format": "bestaudio[ext=m4a]/bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
}