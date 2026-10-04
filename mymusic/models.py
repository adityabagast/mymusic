"""Bentuk data yang dipakai di seluruh aplikasi."""
from bisect import bisect_right
from dataclasses import asdict, dataclass, replace


def _gambar_terbesar(data):
    gambar = data.get("thumbnails") or data.get("thumbnail") or []
    return gambar[-1]["url"] if gambar else ""


def _daftar_artis(data):
    """((nama, id), ...) dari kunci "artists"; id bisa kosong untuk artis yang tidak punya halaman."""
    return tuple((a["name"], a.get("id") or "") for a in data.get("artists") or [] if a.get("name"))


@dataclass(frozen=True)
class Lagu:
    video_id: str
    judul: str
    artis: str
    album: str = ""
    durasi: str = "?"
    sampul: str = ""  # URL gambar sampul
    daftar_artis: tuple = ()  # ((nama, id_artis), ...) untuk tautan; kosong pada data lama
    id_album: str = ""

    @classmethod
    def dari_ytmusic(cls, data):
        """Mengubah dict dari ytmusicapi menjadi Lagu, atau None bila tidak bisa diputar."""
        if not data.get("videoId") or data.get("isAvailable") is False:
            return None
        # Hasil pencarian/playlist memakai "duration" & "thumbnails",
        # sedangkan Mix (get_watch_playlist) memakai "length" & "thumbnail".
        album = data.get("album") or {}
        if isinstance(album, str):
            album = {"name": album}  # lagu dari get_album hanya membawa nama albumnya sebagai teks
        artis = _daftar_artis(data)
        return cls(
            video_id=data["videoId"],
            judul=data.get("title") or "Tanpa judul",
            artis=", ".join(nama for nama, _ in artis),
            album=album.get("name") or "",
            durasi=data.get("duration") or data.get("length") or "?",
            sampul=_gambar_terbesar(data),
            daftar_artis=artis,
            id_album=album.get("id") or "",
        )

    @classmethod
    def dari_dict(cls, data):
        # Data lama tanpa field baru tetap bisa dibaca karena ada nilai bawaan.
        # JSON tidak punya tuple, jadi daftar_artis dikembalikan dari list ke tuple.
        return cls(**dict(data, daftar_artis=tuple(map(tuple, data.get("daftar_artis", ())))))

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


@dataclass(frozen=True)
class InfoArtis:
    """Ringkasan artis untuk kartu (hasil cari, "Penggemar juga menyukai")."""
    id: str
    nama: str
    sampul: str = ""

    @classmethod
    def dari_ytmusic(cls, data):
        # Hasil teratas tidak punya browseId; id & namanya ada di "artists".
        pertama = (data.get("artists") or [{}])[0]
        id_artis = data.get("browseId") or pertama.get("id")
        if not id_artis:
            return None
        nama = (data.get("artist") or data.get("title") or pertama.get("name") or "Artis").strip()
        return cls(id=id_artis, nama=nama, sampul=_gambar_terbesar(data))


@dataclass(frozen=True)
class InfoAlbum:
    """Ringkasan album/single untuk kartu (hasil cari, halaman artis)."""
    id: str
    judul: str
    keterangan: str = ""  # mis. "2022 · Album"
    sampul: str = ""

    @classmethod
    def dari_ytmusic(cls, data):
        if not data.get("browseId"):
            return None
        keterangan = " · ".join(x for x in (data.get("year"), data.get("type")) if x)
        return cls(id=data["browseId"], judul=data.get("title") or "Album", keterangan=keterangan,
                   sampul=_gambar_terbesar(data))


@dataclass(frozen=True)
class Artis:
    """Isi halaman artis."""
    id: str
    nama: str
    pendengar: str = ""  # mis. "57.4M"
    gambar: str = ""  # banner lebar
    lagu: tuple = ()  # lagu populer
    album: tuple = ()  # InfoAlbum
    single: tuple = ()  # InfoAlbum
    serupa: tuple = ()  # InfoArtis

    @classmethod
    def dari_ytmusic(cls, id_artis, data):
        def rak(kunci, jenis):
            return tuple(x for x in map(jenis.dari_ytmusic, (data.get(kunci) or {}).get("results") or []) if x)

        return cls(
            id=id_artis,
            nama=data.get("name") or "Artis",
            pendengar=data.get("monthlyListeners") or "",
            gambar=_gambar_terbesar(data),
            lagu=rak("songs", Lagu),
            album=rak("albums", InfoAlbum),
            single=rak("singles", InfoAlbum),
            serupa=rak("related", InfoArtis),
        )


@dataclass(frozen=True)
class Album:
    """Isi halaman album (album, single, atau EP)."""
    id: str
    judul: str
    jenis: str = "Album"
    tahun: str = ""
    daftar_artis: tuple = ()
    sampul: str = ""
    lagu: tuple = ()

    @classmethod
    def dari_ytmusic(cls, id_album, data):
        judul = data.get("title") or "Album"
        sampul = _gambar_terbesar(data)
        artis = _daftar_artis(data)
        lagu = []
        for satu in filter(None, map(Lagu.dari_ytmusic, data.get("tracks") or [])):
            # Lagu di dalam album tidak membawa sampul & id album sendiri: ambil dari albumnya.
            lagu.append(replace(satu, album=judul, id_album=id_album, sampul=satu.sampul or sampul,
                                daftar_artis=satu.daftar_artis or artis,
                                artis=satu.artis or ", ".join(nama for nama, _ in artis)))
        return cls(id=id_album, judul=judul, jenis=data.get("type") or "Album", tahun=data.get("year") or "",
                   daftar_artis=artis, sampul=sampul, lagu=tuple(lagu))

    @property
    def artis(self):
        return ", ".join(nama for nama, _ in self.daftar_artis)


@dataclass(frozen=True)
class HasilCari:
    """Hasil pencarian: hasil teratas (artis/album, atau None = lagu pertama) + lagu, artis, album."""
    lagu: tuple = ()
    artis: tuple = ()
    album: tuple = ()
    teratas: object = None  # InfoArtis / InfoAlbum / None


@dataclass(frozen=True)
class Lirik:
    """Lirik sebuah lagu. `waktu` berisi waktu mulai (ms) tiap baris; kosong bila lirik tidak bersinkron."""
    baris: tuple = ()
    waktu: tuple = ()
    sumber: str = ""

    @classmethod
    def dari_ytmusic(cls, data):
        """Mengubah hasil get_lyrics() menjadi Lirik (bertimestamp: list LyricLine, biasa: satu string)."""
        sumber = (data.get("source") or "").removeprefix("Source: ")
        if data.get("hasTimestamps"):
            return cls(baris=tuple(baris.text or "♪" for baris in data["lyrics"]),
                       waktu=tuple(baris.start_time for baris in data["lyrics"]),
                       sumber=sumber)
        return cls(baris=tuple((data.get("lyrics") or "").splitlines()), sumber=sumber)

    @property
    def bersinkron(self):
        return bool(self.waktu)

    def indeks_pada(self, milidetik):
        """Indeks baris yang sedang dinyanyikan, atau -1 bila belum sampai baris pertama."""
        return bisect_right(self.waktu, milidetik) - 1
