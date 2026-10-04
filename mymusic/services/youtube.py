"""Semua komunikasi dengan YouTube / YouTube Music ada di file ini."""
import re
from urllib.parse import parse_qs, urlparse

import yt_dlp
from ytmusicapi import YTMusic

from mymusic.config import BATAS_HASIL_CARI, BATAS_LAGU_MIX, BATAS_REKOMENDASI, OPSI_YTDLP
from mymusic.models import InfoPlaylist, Lagu, Lirik

_yt = YTMusic()
_POLA_UKURAN = re.compile(r"=(w\d+-h\d+|s\d+)")


def _jadi_lagu(daftar_mentah):
    """Mengubah list dict ytmusicapi menjadi list Lagu (yang tidak bisa diputar dibuang)."""
    return [lagu for lagu in map(Lagu.dari_ytmusic, daftar_mentah) if lagu]


def cari_lagu(kata_kunci):
    """Mencari lagu, mengembalikan list[Lagu]."""
    return _jadi_lagu(_yt.search(kata_kunci, filter="songs", limit=BATAS_HASIL_CARI))


def adalah_link(teks):
    return teks.startswith(("http://", "https://"))


def ambil_id_playlist(link):
    """Mengambil nilai ?list=... dari link YouTube, atau None bila tidak ada."""
    nilai = parse_qs(urlparse(link).query).get("list")
    return nilai[0] if nilai else None


def ambil_playlist(id_playlist):
    """Mengambil isi playlist, mengembalikan (judul, list[Lagu])."""
    if id_playlist.startswith("RD"):
        # "Mix" buatan YouTube bukan playlist biasa, jadi harus lewat get_watch_playlist.
        data = _yt.get_watch_playlist(playlistId=id_playlist, limit=BATAS_LAGU_MIX)
        return "Mix YouTube", _jadi_lagu(data["tracks"])
    try:
        data = _yt.get_playlist(id_playlist, limit=None)
    except Exception as e:
        raise RuntimeError("Playlist tidak ditemukan atau bersifat privat.") from e
    return data.get("title") or "Playlist", _jadi_lagu(data["tracks"])


def ambil_rekomendasi_lagu(video_id):
    """Lagu yang mirip dengan video_id (radio YouTube Music), tanpa lagu itu sendiri."""
    data = _yt.get_watch_playlist(videoId=video_id, limit=BATAS_REKOMENDASI + 1)
    return [lagu for lagu in _jadi_lagu(data["tracks"]) if lagu.video_id != video_id][:BATAS_REKOMENDASI]


def ambil_playlist_rekomendasi():
    """Playlist dari beranda YouTube Music (bisa tanpa login), mengembalikan list[InfoPlaylist]."""
    hasil = {}
    for rak in _yt.get_home(limit=6):
        for item in rak.get("contents") or []:
            info = InfoPlaylist.dari_ytmusic(item)
            if info:
                hasil.setdefault(info.id, info)
    return list(hasil.values())[:BATAS_REKOMENDASI]


def ambil_lirik(video_id):
    """Lirik sebuah lagu (bertimestamp bila ada), atau None bila YouTube Music tidak punya liriknya."""
    # Lirik tidak bisa dicari langsung dari video_id: ID liriknya ada di data "watch playlist".
    id_lirik = _yt.get_watch_playlist(videoId=video_id, limit=1).get("lyrics")
    if not id_lirik:
        return None
    data = _yt.get_lyrics(id_lirik, timestamps=True)
    return Lirik.dari_ytmusic(data) if data else None


def perbesar_sampul(url, ukuran):
    """Gambar dari server Google bisa diminta dalam ukuran lain dengan mengganti akhiran URL-nya."""
    if not url:
        return url
    return _POLA_UKURAN.sub(
        lambda m: f"=s{ukuran}" if m.group(1).startswith("s") else f"=w{ukuran}-h{ukuran}", url, count=1)


def ambil_url_audio(video_id):
    """Meminta yt-dlp alamat stream audio sebuah lagu (tanpa mengunduh).

    URL ini kedaluwarsa setelah beberapa jam, jadi jangan disimpan.
    """
    with yt_dlp.YoutubeDL(OPSI_YTDLP) as ydl:
        info = ydl.extract_info(f"https://music.youtube.com/watch?v={video_id}", download=False)
    return info["url"]