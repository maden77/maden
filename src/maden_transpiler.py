from maden_parser import *


class Transpiler:
    def __init__(self):
        self.kode = []
        self.indentasi = 0
        self.fungsi_aktif = None
        self.anotasi_aktif = []

    def transpile(self, node) -> str:
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
                if getattr(anotasi, "tipe", None) == "PARALLEL":
                    self.kode.append(self._tab() + f"# @parallel - fungsi {node.nama} akan multi-thread")
                elif getattr(anotasi, "tipe", None) == "ACCELERATOR":
                    self.kode.append(self._tab() + f"# @accelerator(NPU) - fungsi {node.nama} pakai NPU")

            params = ", ".join(self._param_ke_nama(p) for p in node.parameter)
            self.kode.append(self._tab() + f"def {node.nama}({params}):")
            self.indentasi += 1

            if not node.tubuh:
                self.kode.append(self._tab() + "pass")
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
            self.kode.append(self._tab() + f"return {nilai}")
            return None

        if isinstance(node, PernyataanCetak):
            self.kode.append(self._tab() + f"print({self.transpile(node.ekspresi)})")
            return None

        if isinstance(node, PernyataanJika):
            self.kode.append(self._tab() + f"if {self.transpile(node.kondisi)}:")
            self.indentasi += 1
            self._transpile_blok(node.tubuh)
            self.indentasi -= 1

            if node.selain is not None:
                if isinstance(node.selain, PernyataanJika):
                    self.kode.append(self._tab() + f"elif {self.transpile(node.selain.kondisi)}:")
                    self.indentasi += 1
                    self._transpile_blok(node.selain.tubuh)
                    self.indentasi -= 1
                else:
                    self.kode.append(self._tab() + "else:")
                    self.indentasi += 1
                    self._transpile_blok(node.selain)
                    self.indentasi -= 1
            return None

        if isinstance(node, PernyataanUlangi):
            self._transpile_statement(node.inisialisasi)
            self.kode.append(self._tab() + f"while {self.transpile(node.kondisi)}:")
            self.indentasi += 1
            self._transpile_blok(node.tubuh)
            self._transpile_statement(node.iterasi)
            self.indentasi -= 1
            return None

        if isinstance(node, PernyataanUntukSetiap):
            iterable = self.transpile(node.iterable)
            self.kode.append(self._tab() + f"for {node.variabel} in {iterable}:")
            self.indentasi += 1
            self._transpile_blok(node.tubuh)
            self.indentasi -= 1
            return None

        if isinstance(node, PernyataanUlangiSelama):
            self.kode.append(self._tab() + f"while {self.transpile(node.kondisi)}:")
            self.indentasi += 1
            self._transpile_blok(node.tubuh)
            self.indentasi -= 1
            return None

        if isinstance(node, PernyataanImport):
            self.kode.append(self._tab() + f"import {node.modul}")
            return None

        if isinstance(node, EkspresiPenugasan):
            for anotasi in node.anotasi or []:
                if getattr(anotasi, "tipe", None) == "INT8":
                    self.kode.append(self._tab() + f"# @int8 - variabel {node.nama} 8-bit")
                elif getattr(anotasi, "tipe", None) == "INT128":
                    self.kode.append(self._tab() + f"# @int128 - variabel {node.nama} 128-bit")
            self.kode.append(self._tab() + f"{node.nama} = {self.transpile(node.nilai)}")
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
            self.kode.append(self._tab() + "pass")
            return
        for stmt in blok:
            self.transpile(stmt)

    def _transpile_statement(self, node):
        if isinstance(node, EkspresiPenugasan):
            self.kode.append(self._tab() + f"{node.nama} = {self.transpile(node.nilai)}")
        elif isinstance(node, EkspresiPanggilan):
            self.kode.append(self._tab() + self.transpile(node))
        else:
            hasil = self.transpile(node)
            if hasil is not None:
                self.kode.append(self._tab() + str(hasil))

    def _tab(self):
        return "    " * self.indentasi

    @staticmethod
    def _param_ke_nama(param):
        if isinstance(param, str):
            return param
        if isinstance(param, tuple):
            return param[0]
        if hasattr(param, "nilai"):
            return param.nilai
        return str(param)
