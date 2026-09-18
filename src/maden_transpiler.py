from maden_parser import *


class Transpiler:
    """Transpile AST Maden menjadi kode Python yang valid."""

    def __init__(self):
        self.kode = []
        self.indentasi = 0
        self.fungsi_aktif = None
        self.anotasi_aktif = []

    def transpile(self, node) -> str:
        # Setiap proses transpile dimulai dari state yang bersih.
        if isinstance(node, Program):
            self.kode = [
                "# Hasil transpile dari bahasa Maden",
                "# =================================",
            ]
            self.indentasi = 0
            self.fungsi_aktif = None
            self.anotasi_aktif = []
            for stmt in node.pernyataan:
                self.transpile(stmt)
            return "\n".join(self.kode) + "\n"

        if isinstance(node, PernyataanFungsi):
            self.fungsi_aktif = node.nama
            self.anotasi_aktif = node.anotasi

            for anotasi in node.anotasi:
                if anotasi.tipe == "PARALLEL":
                    self.kode.append(self._baris(f"# @parallel - fungsi {node.nama} akan multi-thread"))
                elif anotasi.tipe == "ACCELERATOR":
                    self.kode.append(self._baris(f"# @accelerator(NPU) - fungsi {node.nama} pakai NPU"))

            params = ", ".join(self._nama_parameter(param) for param in node.parameter)
            self.kode.append(self._baris(f"def {node.nama}({params}):"))
            self.indentasi += 1

            if not node.tubuh:
                self.kode.append(self._baris("pass"))
            else:
                for stmt in node.tubuh:
                    self.transpile(stmt)

            self.indentasi -= 1
            self.fungsi_aktif = None
            self.anotasi_aktif = []
            self.kode.append("")
            return None

        if isinstance(node, PernyataanKembali):
            nilai = "None" if node.nilai is None else self.transpile(node.nilai)
            self.kode.append(self._baris(f"return {nilai}"))
            return None

        if isinstance(node, PernyataanCetak):
            self.kode.append(self._baris(f"print({self.transpile(node.ekspresi)})"))
            return None

        if isinstance(node, PernyataanJika):
            self.kode.append(self._baris(f"if {self.transpile(node.kondisi)}:"))
            self.indentasi += 1
            self._transpile_blok(node.tubuh)
            self.indentasi -= 1

            selain = node.selain
            if isinstance(selain, PernyataanJika):
                self.kode.append(self._baris(f"elif {self.transpile(selain.kondisi)}:"))
                self.indentasi += 1
                self._transpile_blok(selain.tubuh)
                self.indentasi -= 1
            elif selain is not None:
                self.kode.append(self._baris("else:"))
                self.indentasi += 1
                self._transpile_blok(selain)
                self.indentasi -= 1
            return None

        if isinstance(node, PernyataanUlangi):
            self._transpile_statement_line(node.inisialisasi)
            self.kode.append(self._baris(f"while {self.transpile(node.kondisi)}:"))
            self.indentasi += 1
            self._transpile_blok(node.tubuh)
            self._transpile_statement_line(node.iterasi)
            self.indentasi -= 1
            return None

        if isinstance(node, PernyataanUntukSetiap):
            self.kode.append(self._baris(
                f"for {node.variabel} in {self.transpile(node.iterable)}:"
            ))
            self.indentasi += 1
            self._transpile_blok(node.tubuh)
            self.indentasi -= 1
            return None

        if isinstance(node, PernyataanUlangiSelama):
            self.kode.append(self._baris(f"while {self.transpile(node.kondisi)}:"))
            self.indentasi += 1
            self._transpile_blok(node.tubuh)
            self.indentasi -= 1
            return None

        if isinstance(node, PernyataanImport):
            self.kode.append(self._baris(f"import {node.modul}"))
            return None

        if isinstance(node, EkspresiPenugasan):
            for anotasi in node.anotasi or []:
                if anotasi.tipe == "INT8":
                    self.kode.append(self._baris(f"# @int8 - variabel {node.nama} 8-bit"))
                elif anotasi.tipe == "INT128":
                    self.kode.append(self._baris(f"# @int128 - variabel {node.nama} 128-bit"))
            self.kode.append(self._baris(f"{node.nama} = {self.transpile(node.nilai)}"))
            return None

        if isinstance(node, EkspresiVariabel):
            return node.nama

        if isinstance(node, EkspresiAngka):
            return repr(node.nilai)

        if isinstance(node, EkspresiTeks):
            return repr(node.nilai)

        if isinstance(node, EkspresiBoolean):
            if node.nilai is True:
                return "True"
            if node.nilai is False:
                return "False"
            return "None"

        if isinstance(node, EkspresiBinOp):
            kiri = self.transpile(node.kiri)
            kanan = self.transpile(node.kanan)
            if node.operator == "not":
                return f"not {kanan}"
            operator = {"&&": "and", "||": "or"}.get(node.operator, node.operator)
            return f"({kiri} {operator} {kanan})"

        if isinstance(node, EkspresiPanggilan):
            argumen = ", ".join(self.transpile(arg) for arg in node.argumen)
            return f"{node.nama}({argumen})"

        raise TypeError(f"Node AST tidak didukung: {type(node).__name__}")

    def _transpile_blok(self, blok):
        if not blok:
            self.kode.append(self._baris("pass"))
            return
        for stmt in blok:
            self.transpile(stmt)

    def _transpile_statement_line(self, node):
        if isinstance(node, EkspresiPenugasan):
            self.kode.append(self._baris(
                f"{node.nama} = {self.transpile(node.nilai)}"
            ))
        elif isinstance(node, EkspresiPanggilan):
            self.kode.append(self._baris(self.transpile(node)))
        else:
            hasil = self.transpile(node)
            if hasil is not None:
                self.kode.append(self._baris(hasil))

    @staticmethod
    def _nama_parameter(parameter):
        if isinstance(parameter, str):
            return parameter
        if isinstance(parameter, tuple):
            return parameter[0]
        return getattr(parameter, "nilai", str(parameter))

    def _baris(self, isi):
        return "    " * self.indentasi + isi
