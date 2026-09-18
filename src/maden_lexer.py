from typing import List


class TokenType:
    FUNGSI = "FUNGSI"
    KEMBALI = "KEMBALI"
    CETAK = "CETAK"
    JIKA = "JIKA"
    SELAIN = "SELAIN"
    ULANGI = "ULANGI"
    UNTUK = "UNTUK"
    SETIAP = "SETIAP"
    DALAM = "DALAM"
    SELAMA = "SELAMA"
    IMPOR = "IMPOR"
    BENAR = "BENAR"
    SALAH = "SALAH"
    KOSONG = "KOSONG"
    DAN = "DAN"
    ATAU = "ATAU"
    NOT = "NOT"

    INT8 = "INT8"
    INT128 = "INT128"
    ACCELERATOR = "ACCELERATOR"
    PRECISION = "PRECISION"
    PARALLEL = "PARALLEL"

    IDENTIFIER = "IDENTIFIER"
    ANGKA = "ANGKA"
    TEKS = "TEKS"
    KURUNG_BUKA = "KURUNG_BUKA"
    KURUNG_TUTUP = "KURUNG_TUTUP"
    KURUNG_KOTAK_BUKA = "KURUNG_KOTAK_BUKA"
    KURUNG_KOTAK_TUTUP = "KURUNG_KOTAK_TUTUP"
    KURUNG_KURUNG_BUKA = "KURUNG_KURUNG_BUKA"
    KURUNG_KURUNG_TUTUP = "KURUNG_KURUNG_TUTUP"
    KOMA = "KOMA"
    TITIK_DUA = "TITIK_DUA"
    TITIK_KOMA = "TITIK_KOMA"
    SAMA_DENGAN = "SAMA_DENGAN"
    TAMBAH = "TAMBAH"
    KURANG = "KURANG"
    KALI = "KALI"
    BAGI = "BAGI"
    MODULUS = "MODULUS"
    LEBIH_BESAR = "LEBIH_BESAR"
    LEBIH_KECIL = "LEBIH_KECIL"
    LEBIH_BESAR_SAMA = "LEBIH_BESAR_SAMA"
    LEBIH_KECIL_SAMA = "LEBIH_KECIL_SAMA"
    SAMA_DENGAN_DUA = "SAMA_DENGAN_DUA"
    TIDAK_SAMA = "TIDAK_SAMA"
    KOMENTAR = "KOMENTAR"
    NEWLINE = "NEWLINE"
    EOF = "EOF"


class Token:
    def __init__(self, tipe: str, nilai, baris: int, kolom: int):
        self.tipe = tipe
        self.nilai = nilai
        self.baris = baris
        self.kolom = kolom

    def __repr__(self):
        return f"Token({self.tipe}, {self.nilai!r}, baris={self.baris})"


class Lexer:
    def __init__(self, kode: str):
        self.kode = kode
        self.pos = 0
        self.baris = 1
        self.kolom = 1
        self.token = []
        self.keyword = {
            "fungsi": TokenType.FUNGSI, "kembali": TokenType.KEMBALI,
            "cetak": TokenType.CETAK, "jika": TokenType.JIKA,
            "selain": TokenType.SELAIN, "ulangi": TokenType.ULANGI,
            "untuk": TokenType.UNTUK, "setiap": TokenType.SETIAP,
            "dalam": TokenType.DALAM, "selama": TokenType.SELAMA,
            "import": TokenType.IMPOR, "benar": TokenType.BENAR,
            "salah": TokenType.SALAH, "kosong": TokenType.KOSONG,
            "dan": TokenType.DAN, "atau": TokenType.ATAU,
            "not": TokenType.NOT, "tidak": TokenType.NOT,
        }
        self.annotations = {
            "@int8": TokenType.INT8, "@int128": TokenType.INT128,
            "@accelerator": TokenType.ACCELERATOR,
            "@precision": TokenType.PRECISION, "@parallel": TokenType.PARALLEL,
        }

    def tokenisasi(self) -> List[Token]:
        while self.pos < len(self.kode):
            char = self.kode[self.pos]
            if char in " \t\r":
                self.pos += 1
                self.kolom += 1
                continue
            if char == "\n":
                self.token.append(Token(TokenType.NEWLINE, "\n", self.baris, self.kolom))
                self.pos += 1
                self.baris += 1
                self.kolom = 1
                continue
            if char == "/" and self._ikuti("/"):
                self.pos += 2
                self.kolom += 2
                while self.pos < len(self.kode) and self.kode[self.pos] != "\n":
                    self.pos += 1
                    self.kolom += 1
                continue
            if char in "\"'":
                self._token_teks(char)
                continue
            # Tanda minus selalu menjadi token operator. Unary minus ditangani parser.
            if char.isdigit():
                self._token_angka()
                continue
            if char.isalpha() or char == "_":
                self._token_identifier()
                continue
            if char == "@":
                self._token_anotasi()
                continue

            operator_dua = {
                "==": (TokenType.SAMA_DENGAN_DUA, "=="),
                "!=": (TokenType.TIDAK_SAMA, "!="),
                ">=": (TokenType.LEBIH_BESAR_SAMA, ">="),
                "<=": (TokenType.LEBIH_KECIL_SAMA, "<="),
                "&&": (TokenType.DAN, "&&"),
                "||": (TokenType.ATAU, "||"),
            }
            pasangan = self.kode[self.pos:self.pos + 2]
            if pasangan in operator_dua:
                tipe, nilai = operator_dua[pasangan]
                self.token.append(Token(tipe, nilai, self.baris, self.kolom))
                self.pos += 2
                self.kolom += 2
                continue

            simbol = {
                "(": TokenType.KURUNG_BUKA, ")": TokenType.KURUNG_TUTUP,
                "[": TokenType.KURUNG_KOTAK_BUKA, "]": TokenType.KURUNG_KOTAK_TUTUP,
                "{": TokenType.KURUNG_KURUNG_BUKA, "}": TokenType.KURUNG_KURUNG_TUTUP,
                ",": TokenType.KOMA, ":": TokenType.TITIK_DUA,
                ";": TokenType.TITIK_KOMA, "=": TokenType.SAMA_DENGAN,
                "+": TokenType.TAMBAH, "-": TokenType.KURANG,
                "*": TokenType.KALI, "/": TokenType.BAGI,
                "%": TokenType.MODULUS, ">": TokenType.LEBIH_BESAR,
                "<": TokenType.LEBIH_KECIL,
            }
            if char in simbol:
                self.token.append(Token(simbol[char], char, self.baris, self.kolom))
                self.pos += 1
                self.kolom += 1
                continue
            raise SyntaxError(f"Karakter tidak dikenal: '{char}' di baris {self.baris}, kolom {self.kolom}")

        self.token.append(Token(TokenType.EOF, None, self.baris, self.kolom))
        return self.token

    def _ikuti(self, nilai: str) -> bool:
        return self.pos + 1 < len(self.kode) and self.kode[self.pos + 1] == nilai

    def _token_teks(self, tanda: str):
        mulai_baris, mulai_kolom = self.baris, self.kolom
        self.pos += 1
        self.kolom += 1
        teks = []
        while self.pos < len(self.kode) and self.kode[self.pos] != tanda:
            if self.kode[self.pos] == "\n":
                self.baris += 1
                self.kolom = 1
            teks.append(self.kode[self.pos])
            self.pos += 1
            self.kolom += 1
        if self.pos >= len(self.kode):
            raise SyntaxError(f"Teks tidak ditutup di baris {mulai_baris}")
        self.pos += 1
        self.kolom += 1
        self.token.append(Token(TokenType.TEKS, "".join(teks), mulai_baris, mulai_kolom))

    def _token_angka(self):
        mulai_baris, mulai_kolom = self.baris, self.kolom
        awal = self.pos
        while self.pos < len(self.kode) and self.kode[self.pos].isdigit():
            self.pos += 1
            self.kolom += 1
        if self.pos < len(self.kode) and self.kode[self.pos] == ".":
            self.pos += 1
            self.kolom += 1
            while self.pos < len(self.kode) and self.kode[self.pos].isdigit():
                self.pos += 1
                self.kolom += 1
        teks = self.kode[awal:self.pos]
        nilai = float(teks) if "." in teks else int(teks)
        self.token.append(Token(TokenType.ANGKA, nilai, mulai_baris, mulai_kolom))

    def _token_identifier(self):
        mulai_baris, mulai_kolom = self.baris, self.kolom
        awal = self.pos
        while self.pos < len(self.kode) and (self.kode[self.pos].isalnum() or self.kode[self.pos] == "_"):
            self.pos += 1
            self.kolom += 1
        asli = self.kode[awal:self.pos]
        identitas = asli.lower()
        tipe = self.keyword.get(identitas, TokenType.IDENTIFIER)
        self.token.append(Token(tipe, identitas if tipe != TokenType.IDENTIFIER else asli, mulai_baris, mulai_kolom))

    def _token_anotasi(self):
        mulai_baris, mulai_kolom = self.baris, self.kolom
        awal = self.pos
        self.pos += 1
        self.kolom += 1
        while self.pos < len(self.kode) and (self.kode[self.pos].isalnum() or self.kode[self.pos] == "_"):
            self.pos += 1
            self.kolom += 1
        anotasi = self.kode[awal:self.pos].lower()
        tipe = self.annotations.get(anotasi)
        if tipe is None:
            raise SyntaxError(f"Anotasi tidak dikenal: '{anotasi}' di baris {mulai_baris}")
        self.token.append(Token(tipe, anotasi, mulai_baris, mulai_kolom))
