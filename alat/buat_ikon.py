"""Membuat ikon aplikasi: mymusic/aset/ikon.svg (sumber) dan ikon.ico (jendela, taskbar, tray, .exe).

Jalankan ulang setelah mengubah warna:  .venv\\Scripts\\python.exe alat\\buat_ikon.py
"""
import struct
import sys
from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

WARNA_LATAR = "#CDBBFF"  # lavender pastel
WARNA_NOT = "#33206E"  # ungu tua, senada dengan latar
UKURAN_ICO = (16, 20, 24, 32, 40, 48, 64, 128, 256)  # ukuran yang dipakai Windows di berbagai tempat
FOLDER_ASET = Path(__file__).resolve().parent.parent / "mymusic" / "aset"


def svg_ikon(ukuran=256):
    """Persegi bulat + not ganda. Di ukuran kecil garisnya lebih tebal agar tidak hilang."""
    tebal = 2.6 if ukuran <= 24 else 2.2
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
        f'<rect x="0.5" y="0.5" width="23" height="23" rx="5.5" fill="{WARNA_LATAR}"/>'
        '<g transform="translate(12 12) scale(0.72) translate(-12.6 -10.6)">'
        f'<path d="M9 17.5V5.2l11-2v12.3" fill="none" stroke="{WARNA_NOT}" stroke-width="{tebal}" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="6.3" cy="17.6" r="2.9" fill="{WARNA_NOT}"/>'
        f'<circle cx="17.3" cy="15.5" r="2.9" fill="{WARNA_NOT}"/>'
        '</g></svg>'
    )


def png_ikon(ukuran):
    """Menggambar ikon di satu ukuran, mengembalikan isi file PNG (bytes)."""
    gambar = QImage(ukuran, ukuran, QImage.Format_ARGB32)
    gambar.fill(Qt.transparent)
    pelukis = QPainter(gambar)
    QSvgRenderer(QByteArray(svg_ikon(ukuran).encode())).render(pelukis)
    pelukis.end()
    penampung = QBuffer()
    penampung.open(QIODevice.WriteOnly)
    gambar.save(penampung, "PNG")
    return bytes(penampung.data())


def tulis_ico(path, daftar_png):
    """File .ico = kepala 6 byte + 16 byte per gambar + isi PNG-nya (format yang didukung sejak Windows Vista)."""
    kepala = struct.pack("<HHH", 0, 1, len(daftar_png))  # 0 = cadangan, 1 = jenis ikon, jumlah gambar
    posisi = 6 + 16 * len(daftar_png)
    direktori, isi = b"", b""
    for ukuran, png in daftar_png:
        sisi = 0 if ukuran >= 256 else ukuran  # 0 berarti 256 di format ICO
        direktori += struct.pack("<BBBBHHII", sisi, sisi, 0, 0, 1, 32, len(png), posisi)
        isi += png
        posisi += len(png)
    path.write_bytes(kepala + direktori + isi)


def main():
    app = QGuiApplication(sys.argv)  # QSvgRenderer & QImage butuh aplikasi Qt
    (FOLDER_ASET / "ikon.svg").write_text(svg_ikon(), encoding="utf-8")
    tulis_ico(FOLDER_ASET / "ikon.ico", [(ukuran, png_ikon(ukuran)) for ukuran in UKURAN_ICO])
    print(f"Ikon dibuat di {FOLDER_ASET}")
    del app


if __name__ == "__main__":
    main()
