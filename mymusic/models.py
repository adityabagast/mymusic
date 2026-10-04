"""Bentuk data yang dipakai di seluruh aplikasi."""
from dataclasses import asdict, dataclass


def _gambar_terbesar(data):
    gambar = data.get("thumbnails") or data.get("thumbnail") or []
    return gambar[-1]["url"] if gambar else ""


@dataclass(frozen=True)
class Lagu:
    video_id: str
    judul: str
    artis: str
    album: str = ""
    durasi: str = "?"
    sampul: str = ""  # URL gambar sampul

    @classmethod
    def dari_ytmusic(cls, data):
        """Mengubah dict dari ytmusicapi menjadi Lagu, atau None bila tidak bisa diputar."""
        if not data.get("videoId") or data.get("isAvailable") is False:
            return None
        # Hasil pencarian/playlist memakai "duration" & "thumbnails",
        # sedangkan Mix (get_watch_playlist) memakai "length" & "thumbnail".
        return cls(
            video_id=data["videoId"],
            judul=data.get("title") or "Tanpa judul",
            artis=", ".join(a["name"] for a in data.get("artists") or []),
            album=(data.get("album") or {}).get("name") or "",
            durasi=data.get("duration") or data.get("length") or "?",
            sampul=_gambar_terbesar(data),
        )

    @classmethod
    def dari_dict(cls, data):
        return cls(**data)  # data lama tanpa "album" tetap bisa dibaca karena ada nilai bawaan

    def ke_dict(self):
        return asdict(self)

    @property
    def teks(self):
        return f"{self.judul} — {self.artis}  ({self.durasi})"

    @property
    def detik(self):
        """Durasi dalam detik ("4:27" -> 267). Durasi yang tidak diketahui dihitung 0."""
        try:
            nilai = 0
            for bagian in self.durasi.split(":"):
                nilai = nilai * 60 + int(bagian)
            return nilai
        except ValueError:
            return 0


@dataclass(frozen=True)
class InfoPlaylist:
    """Ringkasan playlist YouTube Music (isinya diambil terpisah saat dibuka)."""
    id: str
    judul: str
    keterangan: str = ""
    sampul: str = ""

    @classmethod
    def dari_ytmusic(cls, data):
        if not data.get("playlistId"):
            return None
        return cls(
            id=data["playlistId"],
            judul=data.get("title") or "Playlist",
            keterangan=data.get("description") or "",
            sampul=_gambar_terbesar(data),
        )