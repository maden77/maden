from maden_lexer import TokenType, Token


class ASTNode:
    pass


class Program(ASTNode):
    def __init__(self, pernyataan):
        self.pernyataan = pernyataan


class PernyataanFungsi(ASTNode):
    def __init__(self, nama, parameter, tubuh, anotasi=None):
        self.nama = nama
        self.parameter = parameter
        self.tubuh = tubuh
        self.anotasi = anotasi or []


class PernyataanKembali(ASTNode):
    def __init__(self, nilai):
        self.nilai = nilai


class PernyataanCetak(ASTNode):
    def __init__(self, ekspresi):
        self.ekspresi = ekspresi


class PernyataanJika(ASTNode):
    def __init__(self, kondisi, tubuh, selain=None):
        self.kondisi = kondisi
        self.tubuh = tubuh
        self.selain = selain


class PernyataanUlangi(ASTNode):
    def __init__(self, inisialisasi, kondisi, iterasi, tubuh):
        self.inisialisasi = inisialisasi
        self.kondisi = kondisi
        self.iterasi = iterasi
        self.tubuh = tubuh


class PernyataanUntukSetiap(ASTNode):
    def __init__(self, variabel, iterable, tubuh):
        self.variabel = variabel
        self.iterable = iterable
        self.tubuh = tubuh


class PernyataanUlangiSelama(ASTNode):
    def __init__(self, kondisi, tubuh):
        self.kondisi = kondisi
        self.tubuh = tubuh


class PernyataanImport(ASTNode):
    def __init__(self, modul):
        self.modul = modul


class EkspresiVariabel(ASTNode):
    def __init__(self, nama):
        self.nama = nama


class EkspresiAngka(ASTNode):
    def __init__(self, nilai):
        self.nilai = nilai


class EkspresiTeks(ASTNode):
    def __init__(self, nilai):
        self.nilai = nilai


class EkspresiBoolean(ASTNode):
    def __init__(self, nilai):
        self.nilai = nilai


class EkspresiBinOp(ASTNode):
    def __init__(self, kiri, operator, kanan):
        self.kiri = kiri
        self.operator = operator
        self.kanan = kanan


class EkspresiPanggilan(ASTNode):
    def __init__(self, nama, argumen):
        self.nama = nama
        self.argumen = argumen


class EkspresiPenugasan(ASTNode):
    def __init__(self, nama, nilai, anotasi=None):
        self.nama = nama
        self.nilai = nilai
        self.anotasi = anotasi or []


class Parser:
    ANOTASI = (
        TokenType.INT8,
        TokenType.INT128,
        TokenType.ACCELERATOR,
        TokenType.PRECISION,
        TokenType.PARALLEL,
    )

    def __init__(self, token):
        self.token = token
        self.pos = 0

    def parse(self):
        pernyataan = []
        self.lewati_baris_kosong()
        while self.peek().tipe != TokenType.EOF:
            pernyataan.append(self.pernyataan())
            self.lewati_baris_kosong()
        return Program(pernyataan)

    def peek(self):
        return self.token[self.pos]

    def maju(self):
        token = self.peek()
        self.pos += 1
        return token

    def harap(self, tipe, pesan=None):
        if self.peek().tipe == tipe:
            return self.maju()
        if pesan is None:
            pesan = f"Diharapkan {tipe}, dapat {self.peek().tipe}"
        raise SyntaxError(f"{pesan} (baris {self.peek().baris}, kolom {self.peek().kolom})")

    def lewati_baris_kosong(self):
        while self.peek().tipe == TokenType.NEWLINE:
            self.maju()

    def cocok(self, tipe):
        if self.peek().tipe == tipe:
            return self.maju()
        return None

    def pernyataan(self):
        self.lewati_baris_kosong()
        token = self.peek()

        anotasi = []
        while token.tipe in self.ANOTASI:
            anotasi.append(self.maju())
            token = self.peek()

        if token.tipe == TokenType.FUNGSI:
            return self.pernyataan_fungsi(anotasi)

        if token.tipe == TokenType.KEMBALI:
            self.maju()
            if self.peek().tipe in (TokenType.NEWLINE, TokenType.KURUNG_KURUNG_TUTUP, TokenType.EOF):
                self.cocok_newline()
                return PernyataanKembali(None)
            nilai = self.ekspresi()
            self.harap(TokenType.NEWLINE, "Diharapkan baris baru setelah return")
            return PernyataanKembali(nilai)

        if token.tipe == TokenType.CETAK:
            self.maju()
            self.harap(TokenType.KURUNG_BUKA)
            ekspresi = self.ekspresi()
            self.harap(TokenType.KURUNG_TUTUP)
            self.harap(TokenType.NEWLINE, "Diharapkan baris baru setelah cetak")
            return PernyataanCetak(ekspresi)

        if token.tipe == TokenType.JIKA:
            return self.pernyataan_jika()

        if token.tipe == TokenType.ULANGI:
            return self.pernyataan_ulangi()

        if token.tipe == TokenType.UNTUK:
            self.maju()
            self.harap(TokenType.SETIAP)
            nama = self.harap(TokenType.IDENTIFIER).nilai
            self.harap(TokenType.DALAM)
            iterable = self.ekspresi()
            tubuh = self.baca_blok()
            return PernyataanUntukSetiap(nama, iterable, tubuh)

        if token.tipe == TokenType.IMPOR:
            self.maju()
            modul = self.harap(TokenType.IDENTIFIER).nilai
            self.harap(TokenType.NEWLINE)
            return PernyataanImport(modul)

        if token.tipe == TokenType.IDENTIFIER:
            nama = self.maju().nilai
            if self.peek().tipe == TokenType.KURUNG_BUKA:
                return self.baca_panggilan(nama, sebagai_pernyataan=True)
            if self.peek().tipe == TokenType.SAMA_DENGAN:
                self.maju()
                nilai = self.ekspresi()
                self.harap(TokenType.NEWLINE, "Diharapkan baris baru setelah assignment")
                return EkspresiPenugasan(nama, nilai, anotasi)

        if token.tipe == TokenType.NEWLINE:
            self.maju()
            return self.pernyataan()

        raise SyntaxError(f"Pernyataan tidak dikenal: {token}")

    def baca_blok(self):
        self.harap(TokenType.KURUNG_KURUNG_BUKA)
        self.lewati_baris_kosong()
        tubuh = []
        while self.peek().tipe not in (TokenType.KURUNG_KURUNG_TUTUP, TokenType.EOF):
            tubuh.append(self.pernyataan())
            self.lewati_baris_kosong()
        self.harap(TokenType.KURUNG_KURUNG_TUTUP, "Blok belum ditutup dengan '}'")
        self.cocok_newline()
        return tubuh

    def pernyataan_fungsi(self, anotasi):
        self.maju()
        nama = self.harap(TokenType.IDENTIFIER).nilai
        self.harap(TokenType.KURUNG_BUKA)

        parameter = []
        if self.peek().tipe != TokenType.KURUNG_TUTUP:
            while True:
                parameter.append(self.harap(TokenType.IDENTIFIER).nilai)
                if self.peek().tipe == TokenType.TITIK_DUA:
                    self.maju()
                    self.harap(TokenType.IDENTIFIER, "Diharapkan tipe parameter")
                if self.peek().tipe != TokenType.KOMA:
                    break
                self.maju()

        self.harap(TokenType.KURUNG_TUTUP)
        tubuh = self.baca_blok()
        return PernyataanFungsi(nama, parameter, tubuh, anotasi)

    def pernyataan_jika(self):
        self.maju()
        kondisi = self.ekspresi()
        tubuh = self.baca_blok()

        selain = None
        if self.peek().tipe == TokenType.SELAIN:
            self.maju()
            if self.peek().tipe == TokenType.JIKA:
                selain = self.pernyataan_jika()
            else:
                selain = self.baca_blok()

        return PernyataanJika(kondisi, tubuh, selain)

    def pernyataan_ulangi(self):
        self.maju()
        if self.peek().tipe == TokenType.SELAMA:
            self.maju()
            kondisi = self.ekspresi()
            tubuh = self.baca_blok()
            return PernyataanUlangiSelama(kondisi, tubuh)

        self.harap(TokenType.KURUNG_BUKA)
        init = self.ekspresi_penugasan()
        self.harap(TokenType.TITIK_KOMA)
        kondisi = self.ekspresi()
        self.harap(TokenType.TITIK_KOMA)
        iterasi = self.ekspresi()
        self.harap(TokenType.KURUNG_TUTUP)
        tubuh = self.baca_blok()
        return PernyataanUlangi(init, kondisi, iterasi, tubuh)

    def baca_panggilan(self, nama, sebagai_pernyataan=False):
        self.harap(TokenType.KURUNG_BUKA)
        argumen = []
        if self.peek().tipe != TokenType.KURUNG_TUTUP:
            while True:
                argumen.append(self.ekspresi())
                if self.peek().tipe != TokenType.KOMA:
                    break
                self.maju()
        self.harap(TokenType.KURUNG_TUTUP)
        if sebagai_pernyataan:
            self.harap(TokenType.NEWLINE, "Diharapkan baris baru setelah pemanggilan fungsi")
        return EkspresiPanggilan(nama, argumen)

    def cocok_newline(self):
        if self.peek().tipe == TokenType.NEWLINE:
            self.maju()

    def ekspresi(self):
        return self.ekspresi_logika()

    def ekspresi_logika(self):
        kiri = self.ekspresi_perbandingan()
        while self.peek().tipe in (TokenType.DAN, TokenType.ATAU):
            op = self.maju().nilai
            kanan = self.ekspresi_perbandingan()
            kiri = EkspresiBinOp(kiri, op, kanan)
        return kiri

    def ekspresi_perbandingan(self):
        kiri = self.ekspresi_penjumlahan()
        while self.peek().tipe in (
            TokenType.LEBIH_BESAR,
            TokenType.LEBIH_KECIL,
            TokenType.LEBIH_BESAR_SAMA,
            TokenType.LEBIH_KECIL_SAMA,
            TokenType.SAMA_DENGAN_DUA,
            TokenType.TIDAK_SAMA,
        ):
            op = self.maju().nilai
            kanan = self.ekspresi_penjumlahan()
            kiri = EkspresiBinOp(kiri, op, kanan)
        return kiri

    def ekspresi_penjumlahan(self):
        kiri = self.ekspresi_perkalian()
        while self.peek().tipe in (TokenType.TAMBAH, TokenType.KURANG):
            op = self.maju().nilai
            kanan = self.ekspresi_perkalian()
            kiri = EkspresiBinOp(kiri, op, kanan)
        return kiri

    def ekspresi_perkalian(self):
        kiri = self.ekspresi_unary()
        while self.peek().tipe in (TokenType.KALI, TokenType.BAGI, TokenType.MODULUS):
            op = self.maju().nilai
            kanan = self.ekspresi_unary()
            kiri = EkspresiBinOp(kiri, op, kanan)
        return kiri

    def ekspresi_unary(self):
        if self.peek().tipe == TokenType.KURANG:
            self.maju()
            operan = self.ekspresi_unary()
            return EkspresiBinOp(EkspresiAngka(0), '-', operan)
        if self.peek().tipe == TokenType.NOT:
            self.maju()
            operan = self.ekspresi_unary()
            return EkspresiBinOp(EkspresiBoolean(False), 'not', operan)
        return self.ekspresi_primary()

    def ekspresi_primary(self):
        token = self.peek()

        if token.tipe == TokenType.ANGKA:
            self.maju()
            return EkspresiAngka(token.nilai)

        if token.tipe == TokenType.TEKS:
            self.maju()
            return EkspresiTeks(token.nilai)

        if token.tipe == TokenType.BENAR:
            self.maju()
            return EkspresiBoolean(True)

        if token.tipe == TokenType.SALAH:
            self.maju()
            return EkspresiBoolean(False)

        if token.tipe == TokenType.KOSONG:
            self.maju()
            return EkspresiBoolean(None)

        if token.tipe == TokenType.IDENTIFIER:
            nama = self.maju().nilai
            if self.peek().tipe == TokenType.KURUNG_BUKA:
                return self.baca_panggilan(nama)
            return EkspresiVariabel(nama)

        if token.tipe == TokenType.KURUNG_BUKA:
            self.maju()
            nilai = self.ekspresi()
            self.harap(TokenType.KURUNG_TUTUP)
            return nilai

        raise SyntaxError(f"Ekspresi tidak dikenal: {token}")

    def ekspresi_penugasan(self):
        if self.peek().tipe == TokenType.IDENTIFIER:
            nama = self.peek().nilai
            self.maju()
            if self.peek().tipe == TokenType.SAMA_DENGAN:
                self.maju()
                nilai = self.ekspresi()
                return EkspresiPenugasan(nama, nilai)
            return EkspresiVariabel(nama)
        return self.ekspresi()
