"""Antrean lagu beserta mode acak & ulang. Sengaja tanpa Qt supaya mudah diuji dan dikembangkan."""
import random

from mymusic.models import Lagu

ULANG_MATI, ULANG_SEMUA, ULANG_SATU = "mati", "semua", "satu"


class Antrean:
    def __init__(self):
        self.lagu = []
        self.indeks = -1  # posisi lagu yang sedang diputar, -1 = belum ada
        self.acak = False
        self.ulang = ULANG_MATI
        self._asli = []  # urutan sebelum diacak, untuk dikembalikan saat acak dimatikan

    def __len__(self):
        return len(self.lagu)

    @property
    def sekarang(self):
        return self.lagu[self.indeks] if 0 <= self.indeks < len(self.lagu) else None

    def ganti_semua(self, daftar_lagu, mulai=0):
        self.lagu = list(daftar_lagu)
        self.indeks = mulai
        if self.acak:
            self._acak_sisa()

    def tambah(self, lagu):
        self.lagu.append(lagu)

    def sisipkan_berikutnya(self, lagu):
        self.lagu.insert(self.indeks + 1, lagu)

    def hapus(self, posisi):
        """Menghapus lagu di posisi tertentu, sambil menjaga indeks tetap benar."""
        del self.lagu[posisi]
        if posisi < self.indeks:
            self.indeks -= 1
        # Bila yang dihapus adalah lagu yang sedang diputar, indeks kini menunjuk
        # lagu sesudahnya — pemanggil yang memutuskan mau memutarnya atau tidak.

    def pindahkan(self, dari, ke):
        """Memindahkan lagu di posisi `dari` ke depan lagu yang kini ada di posisi `ke` (drag & drop)."""
        if ke in (dari, dari + 1):
            return  # tidak berpindah
        lagu = self.lagu.pop(dari)
        if ke > dari:
            ke -= 1
        self.lagu.insert(ke, lagu)
        if dari == self.indeks:
            self.indeks = ke
        else:
            if dari < self.indeks:
                self.indeks -= 1
            if ke <= self.indeks:
                self.indeks += 1

    def kosongkan(self):
        self.lagu.clear()
        self._asli.clear()
        self.indeks = -1

    def pindah_ke(self, posisi):
        """Pindah ke posisi tertentu. Mengembalikan Lagu-nya, atau None bila di luar batas."""
        if not 0 <= posisi < len(self.lagu):
            return None
        self.indeks = posisi
        return self.lagu[posisi]

    def berikutnya(self):
        if self.indeks + 1 < len(self.lagu):
            return self.pindah_ke(self.indeks + 1)
        if self.ulang == ULANG_SEMUA:
            return self.pindah_ke(0)  # habis: kembali ke awal
        return None

    def sebelumnya(self):
        return self.pindah_ke(self.indeks - 1)

    # ---------- acak ----------

    def atur_acak(self, aktif):
        if aktif == self.acak:
            return
        self.acak = aktif
        if aktif:
            self._acak_sisa()
        else:
            self._kembalikan_urutan()

    def _acak_sisa(self):
        """Lagu yang sedang diputar dipindah ke paling depan, lagu lainnya diacak di belakangnya."""
        self._asli = list(self.lagu)
        sekarang = self.lagu.pop(self.indeks) if self.sekarang is not None else None
        random.shuffle(self.lagu)
        if sekarang is not None:
            self.lagu.insert(0, sekarang)
            self.indeks = 0

    def _kembalikan_urutan(self):
        sekarang = self.sekarang
        sisa = list(self.lagu)
        urutan = []
        for lagu in self._asli:  # urutan lama, hanya lagu yang masih ada di antrean
            for i, kandidat in enumerate(sisa):
                if kandidat is lagu:
                    urutan.append(sisa.pop(i))
                    break
        urutan.extend(sisa)  # lagu yang ditambahkan selama mode acak
        self.lagu = urutan
        self._asli = []
        self.indeks = next((i for i, lagu in enumerate(urutan) if lagu is sekarang), -1)

    # ---------- simpan & pulihkan (untuk sesi) ----------

    def ke_dict(self):
        return {
            "lagu": [lagu.ke_dict() for lagu in self.lagu],
            "indeks": self.indeks,
            "acak": self.acak,
            "ulang": self.ulang,
            # Urutan asli disimpan sebagai posisi di daftar "lagu", agar acak bisa dimatikan setelah dibuka lagi.
            "asli": [next(i for i, x in enumerate(self.lagu) if x is lagu) for lagu in self._asli
                     if any(x is lagu for x in self.lagu)],
        }

    def muat_dict(self, data):
        self.lagu = [Lagu.dari_dict(d) for d in data.get("lagu", [])]
        self.indeks = data.get("indeks", -1) if self.lagu else -1
        self.acak = bool(data.get("acak", False))
        self.ulang = data.get("ulang", ULANG_MATI)
        self._asli = [self.lagu[i] for i in data.get("asli", []) if 0 <= i < len(self.lagu)] if self.acak else []
