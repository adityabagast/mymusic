# Resep PyInstaller untuk membungkus MyMusic menjadi .exe (mode satu folder).
# Bangun dengan:  .venv/Scripts/pyinstaller MyMusic.spec --noconfirm
# Hasil: dist/MyMusic/MyMusic.exe (jalankan dari folder itu; folder _internal/ di sebelahnya wajib ikut).
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

a = Analysis(
    ["main.py"],
    datas=[
        ("mymusic/aset", "mymusic/aset"),  # font & ikon, dibaca lewat path relatif terhadap config.py
        *collect_data_files("ytmusicapi"),  # file bahasa (locales)
        # Versi paket dibaca lewat importlib.metadata (ytdlp_terbaru membandingkan versi bawaan vs unduhan).
        *copy_metadata("yt-dlp"),
        *copy_metadata("ytmusicapi"),
    ],
    excludes=["tkinter"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name="MyMusic",
    icon="mymusic/aset/ikon.ico",
    console=False,  # tanpa jendela terminal hitam
)
coll = COLLECT(exe, a.binaries, a.datas, name="MyMusic")
