"""Memperbarui yt-dlp tanpa membangun ulang aplikasi: versi baru diunduh dari PyPI ke folder data.

Setiap versi punya folder sendiri (FOLDER_YTDLP/<versi>/yt_dlp), jadi yt-dlp yang sedang dipakai
tidak pernah ditimpa. Versi baru mulai dipakai saat aplikasi dibuka ulang.
"""
import hashlib
import importlib.metadata
import io
import json
import re
import shutil
import sys
import urllib.request
import zipfile

from mymusic.config import FOLDER_YTDLP, URL_PYPI_YTDLP


def _angka(versi):
    """'2026.8.19' atau '2026.08.19' -> (2026, 8, 19), agar bisa dibandingkan."""
    return tuple(int(x) for x in re.findall(r"\d+", versi))


def _versi_bawaan():
    """Versi yang terpasang di .venv (atau ikut terbungkus di .exe)."""
    try:
        return importlib.metadata.version("yt-dlp")
    except importlib.metadata.PackageNotFoundError:
        return "0"


def _versi_unduhan():
    """Nama folder versi yang sudah lengkap diunduh, mis. ['2026.9.1']."""
    if not FOLDER_YTDLP.is_dir():
        return []
    return [f.name for f in FOLDER_YTDLP.iterdir() if re.fullmatch(r"[\d.]+", f.name)]


def pakai_ytdlp_terbaru():
    """Panggil SEBELUM `import yt_dlp`: bila hasil unduhan lebih baru dari bawaan, Python memakai itu."""
    terbaru = max(_versi_unduhan(), key=_angka, default=None)
    if terbaru and _angka(terbaru) > _angka(_versi_bawaan()):
        sys.path.insert(0, str(FOLDER_YTDLP / terbaru))  # dicari lebih dulu daripada site-packages


def versi_dipakai():
    """Versi yt-dlp yang sedang berjalan."""
    from yt_dlp.version import __version__
    return __version__


def perbarui():
    """Unduh yt-dlp terbaru dari PyPI. Mengembalikan versi barunya, atau None bila sudah terbaru."""
    with urllib.request.urlopen(URL_PYPI_YTDLP, timeout=15) as respons:
        data = json.load(respons)
    terbaru, dipakai = data["info"]["version"], versi_dipakai()
    if _angka(terbaru) <= _angka(dipakai):
        return None
    if terbaru in _versi_unduhan():
        return terbaru  # sudah diunduh sebelumnya, tinggal buka ulang aplikasi

    wheel = next((u for u in data["urls"] if u["filename"].endswith("-py3-none-any.whl")), None)
    if not wheel:
        raise RuntimeError("Paket yt-dlp yang cocok tidak ditemukan di PyPI.")
    with urllib.request.urlopen(wheel["url"], timeout=60) as respons:
        isi = respons.read()
    if hashlib.sha256(isi).hexdigest() != wheel["digests"]["sha256"]:
        raise RuntimeError("File unduhan rusak (checksum tidak cocok). Coba lagi.")

    # .whl hanyalah file zip; yang dibutuhkan cukup folder yt_dlp/ di dalamnya.
    sementara = FOLDER_YTDLP / "_sementara"
    shutil.rmtree(sementara, ignore_errors=True)
    with zipfile.ZipFile(io.BytesIO(isi)) as z:
        z.extractall(sementara, [nama for nama in z.namelist() if nama.startswith("yt_dlp/")])
    # Versi lama dibuang, kecuali yang sedang dipakai (aplikasi yang berjalan masih bisa membaca file-nya).
    for versi in _versi_unduhan():
        if _angka(versi) != _angka(dipakai):
            shutil.rmtree(FOLDER_YTDLP / versi, ignore_errors=True)
    # Diganti nama paling akhir, jadi unduhan yang terputus di tengah jalan tidak pernah terpakai.
    sementara.rename(FOLDER_YTDLP / terbaru)
    return terbaru
