import re
from typing import List, Tuple, Optional

# Jenis-jenis token
class TokenType:
    # Kata kunci
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
    
    # Tipe data & anotasi
    INT8 = "INT8"
    INT128 = "INT128"
    ACCELERATOR = "ACCELERATOR"
    PRECISION = "PRECISION"
    PARALLEL = "PARALLEL"
    
    # Simbol
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
    DAN = "DAN"
    ATAU = "ATAU"
    NOT = "NOT"
    KOMENTAR = "KOMENTAR"
    NEWLINE = "NEWLINE"
    EOF = "EOF"

class Token:
    def __init__(self, tipe: str, nilai: any, baris: int, kolom: int):
        self.tipe = tipe
        self.nilai = nilai
        self.baris = baris
        self.kolom = kolom
    
    def __repr__(self):
        return f"Token({self.tipe}, {repr(self.nilai)}, baris={self.baris})"

class Lexer:
    def __init__(self, kode: str):
        self.kode = kode
        self.pos = 0
        self.baris = 1
        self.kolom = 1
        self.token = []
        
        # Kata kunci
        self.keyword = {
            "fungsi": TokenType.FUNGSI,
            "kembali": TokenType.KEMBALI,
            "cetak": TokenType.CETAK,
            "jika": TokenType.JIKA,
            "Selain": TokenType.SELAIN,
            "ulangi": TokenType.ULANGI,
            "untuk": TokenType.UNTUK,
            "setiap": TokenType.SETIAP,
            "dalam": TokenType.DALAM,
            "selama": TokenType.SELAMA,
            "import": TokenType.IMPOR,
            "benar": TokenType.BENAR,
            "salah": TokenType.SALAH,
            "kosong": TokenType.KOSONG,
        }
        
        # Anotasi
        self.annotations = {
            "@int8": TokenType.INT8,
            "@int128": TokenType.INT128,
            "@accelerator": TokenType.ACCELERATOR,
            "@precision": TokenType.PRECISION,
            "@parallel": TokenType.PARALLEL,
        }
    
    def tokenisasi(self) -> List[Token]:
        while self.pos < len(self.kode):
            char = self.kode[self.pos]
            
            # Abaikan spasi
            if char == ' ' or char == '\t':
                self.pos += 1
                self.kolom += 1
                continue
            
            # Baris baru
            if char == '\n':
                self.token.append(Token(TokenType.NEWLINE, '\n', self.baris, self.kolom))
                self.pos += 1
                self.baris += 1
                self.kolom = 1
                continue
            
            # Komentar
            if char == '/' and self.pos + 1 < len(self.kode) and self.kode[self.pos + 1] == '/':
                self.pos += 2
                while self.pos < len(self.kode) and self.kode[self.pos] != '\n':
                    self.pos += 1
                continue
            
            # Teks (string)
            if char == '"' or char == "'":
                return self._token_teks(char)
            
            # Angka
            if char.isdigit() or (char == '-' and self.pos + 1 < len(self.kode) and self.kode[self.pos + 1].isdigit()):
                return self._token_angka()
            
            # Identifier atau kata kunci
            if char.isalpha() or char == '_':
                return self._token_identifier()
            
            # Anotasi @
            if char == '@':
                return self._token_anotasi()
            
            # Simbol satu karakter
            simbol_map = {
                '(': TokenType.KURUNG_BUKA,
                ')': TokenType.KURUNG_TUTUP,
                '[': TokenType.KURUNG_KOTAK_BUKA,
                ']': TokenType.KURUNG_KOTAK_TUTUP,
                '{': TokenType.KURUNG_KURUNG_BUKA,
                '}': TokenType.KURUNG_KURUNG_TUTUP,
                ',': TokenType.KOMA,
                ':': TokenType.TITIK_DUA,
                ';': TokenType.TITIK_KOMA,
                '+': TokenType.TAMBAH,
                '-': TokenType.KURANG,
                '*': TokenType.KALI,
                '/': TokenType.BAGI,
                '%': TokenType.MODULUS,
            }
            
            if char in simbol_map:
                self.token.append(Token(simbol_map[char], char, self.baris, self.kolom))
                self.pos += 1
                self.kolom += 1
                continue
            
            # Simbol dua karakter
            if char == '=' and self.pos + 1 < len(self.kode) and self.kode[self.pos + 1] == '=':
                self.token.append(Token(TokenType.SAMA_DENGAN_DUA, '==', self.baris, self.kolom))
                self.pos += 2
                self.kolom += 2
                continue
            
            if char == '!' and self.pos + 1 < len(self.kode) and self.kode[self.pos + 1] == '=':
                self.token.append(Token(TokenType.TIDAK_SAMA, '!=', self.baris, self.kolom))
                self.pos += 2
                self.kolom += 2
                continue
            
            if char == '>' and self.pos + 1 < len(self.kode) and self.kode[self.pos + 1] == '=':
                self.token.append(Token(TokenType.LEBIH_BESAR_SAMA, '>=', self.baris, self.kolom))
                self.pos += 2
                self.kolom += 2
                continue
            
            if char == '<' and self.pos + 1 < len(self.kode) and self.kode[self.pos + 1] == '=':
                self.token.append(Token(TokenType.LEBIH_KECIL_SAMA, '<=', self.baris, self.kolom))
                self.pos += 2
                self.kolom += 2
                continue
            
            if char == '=':
                self.token.append(Token(TokenType.SAMA_DENGAN, '=', self.baris, self.kolom))
                self.pos += 1
                self.kolom += 1
                continue
            
            # Operator logika
            if char == '&' and self.pos + 1 < len(self.kode) and self.kode[self.pos + 1] == '&':
                self.token.append(Token(TokenType.DAN, '&&', self.baris, self.kolom))
                self.pos += 2
                self.kolom += 2
                continue
            
            if char == '|' and self.pos + 1 < len(self.kode) and self.kode[self.pos + 1] == '|':
                self.token.append(Token(TokenType.ATAU, '||', self.baris, self.kolom))
                self.pos += 2
                self.kolom += 2
                continue
            
            # Error
            raise SyntaxError(f"Karakter tidak dikenal: '{char}' di baris {self.baris}, kolom {self.kolom}")
        
        self.token.append(Token(TokenType.EOF, None, self.baris, self.kolom))
        return self.token
    
    def _token_teks(self, tanda: str):
        self.pos += 1
        self.kolom += 1
        mulai_baris = self.baris
        mulai_kolom = self.kolom
        teks = ""
        
        while self.pos < len(self.kode) and self.kode[self.pos] != tanda:
            if self.kode[self.pos] == '\n':
                self.baris += 1
                self.kolom = 1
            teks += self.kode[self.pos]
            self.pos += 1
            self.kolom += 1
        
        if self.pos >= len(self.kode):
            raise SyntaxError(f"Teks tidak ditutup di baris {mulai_baris}")
        
        self.pos += 1  # Lewati tanda tutup
        self.kolom += 1
        self.token.append(Token(TokenType.TEKS, teks, mulai_baris, mulai_kolom))
    
    def _token_angka(self):
        mulai_baris = self.baris
        mulai_kolom = self.kolom
        angka = ""
        
        # Tanda negatif
        if self.kode[self.pos] == '-':
            angka += '-'
            self.pos += 1
            self.kolom += 1
        
        # Angka bulat
        while self.pos < len(self.kode) and self.kode[self.pos].isdigit():
            angka += self.kode[self.pos]
            self.pos += 1
            self.kolom += 1
        
        # Pecahan
        if self.pos < len(self.kode) and self.kode[self.pos] == '.':
            angka += '.'
            self.pos += 1
            self.kolom += 1
            while self.pos < len(self.kode) and self.kode[self.pos].isdigit():
                angka += self.kode[self.pos]
                self.pos += 1
                self.kolom += 1
        
        # Ubah ke float atau int
        if '.' in angka:
            nilai = float(angka)
        else:
            nilai = int(angka)
        
        self.token.append(Token(TokenType.ANGKA, nilai, mulai_baris, mulai_kolom))
    
    def _token_identifier(self):
        mulai_baris = self.baris
        mulai_kolom = self.kolom
        identitas = ""
        
        while self.pos < len(self.kode) and (self.kode[self.pos].isalnum() or self.kode[self.pos] == '_'):
            identitas += self.kode[self.pos]
            self.pos += 1
            self.kolom += 1
        
        # Cek apakah ini kata kunci
        tipe = self.keyword.get(identitas, TokenType.IDENTIFIER)
        self.token.append(Token(tipe, identitas, mulai_baris, mulai_kolom))
    
    def _token_anotasi(self):
        mulai_baris = self.baris
        mulai_kolom = self.kolom
        anotasi = "@"
        self.pos += 1
        self.kolom += 1
        
        while self.pos < len(self.kode) and (self.kode[self.pos].isalpha() or self.kode[self.pos] == '_'):
            anotasi += self.kode[self.pos]
            self.pos += 1
            self.kolom += 1
        
        tipe = self.annotations.get(anotasi)
        if tipe:
            self.token.append(Token(tipe, anotasi, mulai_baris, mulai_kolom))
        else:
            raise SyntaxError(f"Anotasi tidak dikenal: '{anotasi}' di baris {mulai_baris}")
