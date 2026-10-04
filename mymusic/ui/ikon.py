"""Ikon garis (SVG) yang sama dengan prototipe, digambar dalam warna apa pun."""
from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QGuiApplication, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from mymusic.ui.tema import TEKS_REDUP

# Isi <svg> berukuran 24x24. Bentuk yang diisi penuh memakai fill="currentColor".
_IKON = {
    "cari": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "rumah": '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>',
    "koleksi": '<path d="M4 3v18M9 3v18"/><path d="m14 3.5 6 17"/>',
    "tambah": '<path d="M12 5v14M5 12h14"/>',
    "putar": '<path d="M7 4v16l13-8z" fill="currentColor" stroke="none"/>',
    "jeda": '<rect x="6" y="4" width="4" height="16" rx="1" fill="currentColor" stroke="none"/>'
            '<rect x="14" y="4" width="4" height="16" rx="1" fill="currentColor" stroke="none"/>',
    "sebelum": '<path d="M19 20 9 12l10-8v16z" fill="currentColor" stroke="none"/>'
               '<rect x="4" y="4" width="2.5" height="16" rx="1" fill="currentColor" stroke="none"/>',
    "berikut": '<path d="m5 4 10 8-10 8V4z" fill="currentColor" stroke="none"/>'
               '<rect x="17.5" y="4" width="2.5" height="16" rx="1" fill="currentColor" stroke="none"/>',
    "acak": '<path d="M2 18h1.4c1.3 0 2.5-.6 3.3-1.7l6.1-8.6c.7-1.1 2-1.7 3.3-1.7H22"/><path d="m18 2 4 4-4 4"/>'
            '<path d="M2 6h1.9c1.5 0 2.9.9 3.6 2.2"/><path d="M22 18h-5.9c-1.3 0-2.6-.7-3.3-1.8l-.5-.8"/>'
            '<path d="m18 14 4 4-4 4"/>',
    "ulang": '<path d="m17 2 4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="m7 22-4-4 4-4"/>'
             '<path d="M21 13v1a4 4 0 0 1-4 4H3"/>',
    "ulang_satu": '<path d="m17 2 4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="m7 22-4-4 4-4"/>'
                  '<path d="M21 13v1a4 4 0 0 1-4 4H3"/><path d="M11 10h1v4"/>',
    "volume": '<path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M19 5a10 10 0 0 1 0 14"/>',
    "speaker": '<path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/>',
    "antrean": '<path d="M3 6h13M3 12h13M3 18h8"/><circle cx="17" cy="18" r="2"/><path d="M19 18V9l3 1"/>',
    "tambah_antrean": '<path d="M3 6h13M3 12h13M3 18h8"/><path d="M19 15v6M16 18h6"/>',
    "sedang_diputar": '<rect x="3" y="3" width="18" height="18" rx="2"/>'
                      '<path d="m10 8 6 4-6 4z" fill="currentColor" stroke="none"/>',
    "titik": '<circle cx="5" cy="12" r="2" fill="currentColor" stroke="none"/>'
             '<circle cx="12" cy="12" r="2" fill="currentColor" stroke="none"/>'
             '<circle cx="19" cy="12" r="2" fill="currentColor" stroke="none"/>',
    "tutup": '<path d="M18 6 6 18M6 6l12 12"/>',
    "hapus": '<path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/>'
            '<path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/>',
    "simpan": '<circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/>',
    "not": '<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>',
    "jam": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "hati": '<path d="M19 14c1.5-1.5 3-3.2 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.8 0-3 .5-4.5 2-1.5-1.5-2.7-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4 3 5.5l7 7z"/>',
    "hati_penuh": '<path d="M19 14c1.5-1.5 3-3.2 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.8 0-3 .5-4.5 2-1.5-1.5-2.7-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4 3 5.5l7 7z" fill="currentColor"/>',
    "mikrofon": '<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M19 10v1a7 7 0 0 1-14 0v-1M12 18v4"/>',
}


def pixmap_ikon(nama, warna=TEKS_REDUP, ukuran=20, tebal=2):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{warna}" '
           f'stroke-width="{tebal}" stroke-linecap="round" stroke-linejoin="round">'
           f'{_IKON[nama].replace("currentColor", warna)}</svg>')
    rasio = QGuiApplication.primaryScreen().devicePixelRatio() if QGuiApplication.primaryScreen() else 1
    gambar = QPixmap(int(ukuran * rasio), int(ukuran * rasio))
    gambar.fill(Qt.transparent)
    pelukis = QPainter(gambar)
    QSvgRenderer(QByteArray(svg.encode())).render(pelukis)
    pelukis.end()
    gambar.setDevicePixelRatio(rasio)  # agar tetap tajam di layar dengan skala 125%/150%
    return gambar


def ikon(nama, warna=TEKS_REDUP, ukuran=20, tebal=2):
    return QIcon(pixmap_ikon(nama, warna, ukuran, tebal))
