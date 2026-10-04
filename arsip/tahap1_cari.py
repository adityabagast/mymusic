from ytmusicapi import YTMusic

yt = YTMusic()

def cari_lagu(kata_kunci):
    """Mencari lagu dan mengembalikan daftar hasil (list of dict)."""
    return yt.search(kata_kunci, filter="songs", limit=10)

def tampilkan(daftar_lagu):
    """Mencetak hasil pencarian dengan rapi."""
    for nomor, lagu in enumerate(daftar_lagu, start=1):
        judul = lagu["title"]
        artis = ", ".join(a["name"] for a in lagu.get("artists", []))
        durasi = lagu.get("duration", "?")
        print(f"{nomor:2}. {judul} - {artis} ({durasi})")

def main():
    while True:
        kata = input("\nCari lagu (Enter kosong untuk keluar): ").strip()
        if not kata:
            print("Sampai Jumpa!")
            break

        hasil = cari_lagu(kata)
        if not hasil:
            print("Tidak ada hasil.")
            continue

        tampilkan(hasil)

if __name__ == "__main__":
    main()