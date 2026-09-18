# maden_parser_v2.py
from maden_lexer import TokenType, Token
from maden_types import Tipe, TipeData, TabelSimbol, infer_tipe


class ASTNode:
    pass


# Tambahan node untuk tipe
class PernyataanDeklarasi(ASTNode):
    def __init__(self, nama, tipe, nilai=None, anotasi=None):
        self.nama = nama
        self.tipe = tipe
        self.nilai = nilai
        self.anotasi = anotasi or []


class Program(ASTNode):
    def __init__(self, pernyataan):
        self.pernyataan = pernyataan


class PernyataanFungsi(ASTNode):
    def __init__(self, nama, parameter, tipe_kembali, tubuh, anotasi=None):
        self.nama = nama
        self.parameter = parameter
        self.tipe_kembali = tipe_kembali
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
    def __init__(self, nilai, tipe=None):
        self.nilai = nilai
        self.tipe = tipe or infer_tipe(nilai)


class EkspresiTeks(ASTNode):
    def __init__(self, nilai):
        self.nilai = nilai
        self.tipe = Tipe(TipeData.STRING)


class EkspresiBoolean(ASTNode):
    def __init__(self, nilai):
        self.nilai = nilai
        self.tipe = Tipe(TipeData.BOOL)


class EkspresiArray(ASTNode):
    def __init__(self, elemen):
        self.elemen = elemen
        self.tipe = Tipe(TipeData.ARRAY, Tipe(TipeData.KOSONG))
        if elemen:
            self.tipe = Tipe(TipeData.ARRAY, infer_tipe(elemen[0]))


class EkspresiBinOp(ASTNode):
    def __init__(self, kiri, operator, kanan):
        self.kiri = kiri
        self.operator = operator
        self.kanan = kanan
        self.tipe = None


class EkspresiPanggilan(ASTNode):
    def __init__(self, nama, argumen):
        self.nama = nama
        self.argumen = argumen
        self.tipe = None


class EkspresiPenugasan(ASTNode):
    def __init__(self, nama, nilai, anotasi=None):
        self.nama = nama
        self.nilai = nilai
        self.anotasi = anotasi or []
        self.tipe = None


class ParserV2:
    def __init__(self, token):
        self.token = token
        self.pos = 0
        self.tabel_simbol = TabelSimbol()
        self.fungsi_aktif = None

    def parse(self) -> Program:
        pernyataan = []
        while self.peek().tipe != TokenType.EOF:
            pernyataan.append(self.pernyataan())
        return Program(pernyataan)

    def peek(self) -> Token:
        return self.token[self.pos]

    def maju(self):
        self.pos += 1

    def cocok(self, tipe):
        if self.peek().tipe == tipe:
            return self.maju()
        return None

    def harap(self, tipe, pesan=None):
        if self.peek().tipe == tipe:
            return self.maju()
        if pesan is None:
            pesan = f"Diharapkan {tipe}, dapat {self.peek().tipe}"
        raise SyntaxError(pesan)

    def pernyataan(self):
        token = self.peek()

        anotasi = []
        while token.tipe in [
            TokenType.INT8,
            TokenType.INT128,
            TokenType.ACCELERATOR,
            TokenType.PRECISION,
            TokenType.PARALLEL,
        ]:
            anotasi.append(token)
            self.maju()
            token = self.peek()

        if token.tipe == TokenType.FUNGSI:
            return self.pernyataan_fungsi(anotasi)

        if token.tipe == TokenType.KEMBALI:
            self.maju()
            if self.peek().tipe == TokenType.NEWLINE:
                self.harap(TokenType.NEWLINE)
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
            self.maju()
            kondisi = self.ekspresi()
            self.harap(TokenType.KURUNG_KURUNG_BUKA)
            tubuh = self.blok()
            self.harap(TokenType.KURUNG_KURUNG_TUTUP)

            selain = None
            if self.peek().tipe == TokenType.SELAIN:
                self.maju()
                if self.peek().tipe == TokenType.JIKA:
                    self.maju()
                    kondisi_else = self.ekspresi()
                    self.harap(TokenType.KURUNG_KURUNG_BUKA)
                    tubuh_else = self.blok()
                    self.harap(TokenType.KURUNG_KURUNG_TUTUP)
                    selain = PernyataanJika(kondisi_else, tubuh_else, None)
                else:
                    self.harap(TokenType.KURUNG_KURUNG_BUKA)
                    tubuh_else = self.blok()
                    self.harap(TokenType.KURUNG_KURUNG_TUTUP)
                    selain = tubuh_else

            return PernyataanJika(kondisi, tubuh, selain)

        if token.tipe == TokenType.ULANGI:
            self.maju()
            if self.peek().tipe == TokenType.SELAMA:
                self.maju()
                kondisi = self.ekspresi()
                self.harap(TokenType.KURUNG_KURUNG_BUKA)
                tubuh = self.blok()
                self.harap(TokenType.KURUNG_KURUNG_TUTUP)
                return PernyataanUlangiSelama(kondisi, tubuh)

            self.harap(TokenType.KURUNG_BUKA)
            inisialisasi = self.ekspresi_penugasan()
            self.harap(TokenType.TITIK_KOMA)
            kondisi = self.ekspresi()
            self.harap(TokenType.TITIK_KOMA)
            iterasi = self.ekspresi()
            self.harap(TokenType.KURUNG_TUTUP)
            self.harap(TokenType.KURUNG_KURUNG_BUKA)
            tubuh = self.blok()
            self.harap(TokenType.KURUNG_KURUNG_TUTUP)
            return PernyataanUlangi(inisialisasi, kondisi, iterasi, tubuh)

        if token.tipe == TokenType.UNTUK:
            self.maju()
            self.harap(TokenType.SETIAP)
            variabel = self.harap(TokenType.IDENTIFIER).nilai
            self.harap(TokenType.DALAM)
            iterable = self.ekspresi()
            self.harap(TokenType.KURUNG_KURUNG_BUKA)
            tubuh = self.blok()
            self.harap(TokenType.KURUNG_KURUNG_TUTUP)
            return PernyataanUntukSetiap(variabel, iterable, tubuh)

        if token.tipe == TokenType.IMPOR:
            self.maju()
            modul = self.harap(TokenType.IDENTIFIER).nilai
            self.harap(TokenType.NEWLINE)
            return PernyataanImport(modul)

        if token.tipe == TokenType.IDENTIFIER:
            nama = token.nilai
            self.maju()

            if self.peek().tipe == TokenType.KURUNG_BUKA:
                self.maju()
                argumen = []
                if self.peek().tipe != TokenType.KURUNG_TUTUP:
                    argumen.append(self.ekspresi())
                    while self.peek().tipe == TokenType.KOMA:
                        self.maju()
                        argumen.append(self.ekspresi())
                self.harap(TokenType.KURUNG_TUTUP)
                self.harap(TokenType.NEWLINE)
                return EkspresiPanggilan(nama, argumen)

            if self.peek().tipe == TokenType.SAMA_DENGAN:
                self.maju()
                nilai = self.ekspresi()
                self.harap(TokenType.NEWLINE)
                simbol = self.tabel_simbol.cari(nama)
                if simbol is None:
                    tipe = infer_tipe(nilai.nilai if hasattr(nilai, 'nilai') else None)
                    self.tabel_simbol.tambah(nama, tipe, None, anotasi)
                return EkspresiPenugasan(nama, nilai, anotasi)

        if token.tipe == TokenType.NEWLINE:
            self.maju()
            return self.pernyataan()

        raise SyntaxError(f"Pernyataan tidak dikenal: {token}")

    def blok(self):
        pernyataan = []
        self.tabel_simbol.masuk_scope()
        while self.peek().tipe != TokenType.KURUNG_KURUNG_TUTUP and self.peek().tipe != TokenType.EOF:
            pernyataan.append(self.pernyataan())
        self.tabel_simbol.keluar_scope()
        return pernyataan

    def pernyataan_fungsi(self, anotasi):
        self.maju()
        nama = self.harap(TokenType.IDENTIFIER).nilai
        self.harap(TokenType.KURUNG_BUKA)

        parameter = []
        if self.peek().tipe != TokenType.KURUNG_TUTUP:
            param_nama = self.harap(TokenType.IDENTIFIER).nilai
            if self.peek().tipe == TokenType.TITIK_DUA:
                self.maju()
                if self.peek().tipe == TokenType.IDENTIFIER:
                    self.maju()
            parameter.append((param_nama, self.peek().nilai if self.peek().tipe == TokenType.IDENTIFIER else None))

            while self.peek().tipe == TokenType.KOMA:
                self.maju()
                param_nama = self.harap(TokenType.IDENTIFIER).nilai
                if self.peek().tipe == TokenType.TITIK_DUA:
                    self.maju()
                    if self.peek().tipe == TokenType.IDENTIFIER:
                        self.maju()
                parameter.append((param_nama, self.peek().nilai if self.peek().tipe == TokenType.IDENTIFIER else None))

        self.harap(TokenType.KURUNG_TUTUP)
        tipe_kembali = Tipe(TipeData.KOSONG)
        if self.peek().tipe == TokenType.TITIK_DUA:
            self.maju()
            tipe_kembali = self.baca_tipe()

        self.harap(TokenType.KURUNG_KURUNG_BUKA)
        self.tabel_simbol.masuk_scope()
        for param_nama, param_tipe in parameter:
            self.tabel_simbol.tambah(param_nama, param_tipe if isinstance(param_tipe, Tipe) else Tipe(TipeData.KOSONG))
        tubuh = self.blok()
        self.tabel_simbol.keluar_scope()
        self.harap(TokenType.KURUNG_KURUNG_TUTUP)
        return PernyataanFungsi(nama, parameter, tipe_kembali, tubuh, anotasi)

    def baca_tipe(self) -> Tipe:
        token = self.peek()
        if token.tipe == TokenType.IDENTIFIER:
            tipe_str = token.nilai
            self.maju()

            if self.peek().tipe == TokenType.KURUNG_KOTAK_BUKA:
                self.maju()
                self.harap(TokenType.KURUNG_KOTAK_TUTUP)
                if tipe_str == "int":
                    return Tipe(TipeData.ARRAY, Tipe(TipeData.INT))
                elif tipe_str == "float":
                    return Tipe(TipeData.ARRAY, Tipe(TipeData.FLOAT))
                elif tipe_str == "string":
                    return Tipe(TipeData.ARRAY, Tipe(TipeData.STRING))
                elif tipe_str == "bool":
                    return Tipe(TipeData.ARRAY, Tipe(TipeData.BOOL))

            if tipe_str == "int":
                return Tipe(TipeData.INT)
            elif tipe_str == "float":
                return Tipe(TipeData.FLOAT)
            elif tipe_str == "string":
                return Tipe(TipeData.STRING)
            elif tipe_str == "bool":
                return Tipe(TipeData.BOOL)
            elif tipe_str == "kosong":
                return Tipe(TipeData.KOSONG)

        raise SyntaxError(f"Tipe tidak dikenal: {token}")

    def ekspresi(self):
        return self.ekspresi_logika()

    def ekspresi_logika(self):
        kiri = self.ekspresi_perbandingan()
        while self.peek().tipe in [TokenType.DAN, TokenType.ATAU]:
            operator = self.peek()
            self.maju()
            kanan = self.ekspresi_perbandingan()
            kiri = EkspresiBinOp(kiri, operator.nilai, kanan)
        return kiri

    def ekspresi_perbandingan(self):
        kiri = self.ekspresi_penjumlahan()
        while self.peek().tipe in [
            TokenType.LEBIH_BESAR,
            TokenType.LEBIH_KECIL,
            TokenType.LEBIH_BESAR_SAMA,
            TokenType.LEBIH_KECIL_SAMA,
            TokenType.SAMA_DENGAN_DUA,
            TokenType.TIDAK_SAMA,
        ]:
            operator = self.peek()
            self.maju()
            kanan = self.ekspresi_penjumlahan()
            kiri = EkspresiBinOp(kiri, operator.nilai, kanan)
        return kiri

    def ekspresi_penjumlahan(self):
        kiri = self.ekspresi_perkalian()
        while self.peek().tipe in [TokenType.TAMBAH, TokenType.KURANG]:
            operator = self.peek()
            self.maju()
            kanan = self.ekspresi_perkalian()
            kiri = EkspresiBinOp(kiri, operator.nilai, kanan)
        return kiri

    def ekspresi_perkalian(self):
        kiri = self.ekspresi_unary()
        while self.peek().tipe in [TokenType.KALI, TokenType.BAGI, TokenType.MODULUS]:
            operator = self.peek()
            self.maju()
            kanan = self.ekspresi_unary()
            kiri = EkspresiBinOp(kiri, operator.nilai, kanan)
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
            nama = token.nilai
            self.maju()

            if self.peek().tipe == TokenType.KURUNG_BUKA:
                self.maju()
                argumen = []
                if self.peek().tipe != TokenType.KURUNG_TUTUP:
                    argumen.append(self.ekspresi())
                    while self.peek().tipe == TokenType.KOMA:
                        self.maju()
                        argumen.append(self.ekspresi())
                self.harap(TokenType.KURUNG_TUTUP)
                return EkspresiPanggilan(nama, argumen)

            return EkspresiVariabel(nama)

        if token.tipe == TokenType.KURUNG_KOTAK_BUKA:
            self.maju()
            elemen = []
            if self.peek().tipe != TokenType.KURUNG_KOTAK_TUTUP:
                elemen.append(self.ekspresi())
                while self.peek().tipe == TokenType.KOMA:
                    self.maju()
                    elemen.append(self.ekspresi())
            self.harap(TokenType.KURUNG_KOTAK_TUTUP)
            return EkspresiArray(elemen)

        if token.tipe == TokenType.KURUNG_BUKA:
            self.maju()
            ekspresi = self.ekspresi()
            self.harap(TokenType.KURUNG_TUTUP)
            return ekspresi

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
