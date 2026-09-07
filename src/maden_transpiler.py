from maden_parser import *

class Transpiler:
    def __init__(self):
        self.kode = []
        self.indentasi = 0
        self.fungsi_aktif = None
        self.anotasi_aktif = []
    
    def transpile(self, node) -> str:
        if isinstance(node, Program):
            self.kode.append("# Hasil transpile dari bahasa Maden")
            self.kode.append("# =================================")
            for stmt in node.pernyataan:
                self.transpile(stmt)
            return "\n".join(self.kode)
        
        elif isinstance(node, PernyataanFungsi):
            self.fungsi_aktif = node.nama
            self.anotasi_aktif = node.anotasi
            
            # Cek anotasi
            for anotasi in node.anotasi:
                if anotasi.tipe == "PARALLEL":
                    self.kode.append(self._tab() + f"# @parallel - fungsi {node.nama} akan multi-thread")
                elif anotasi.tipe == "ACCELERATOR":
                    self.kode.append(self._tab() + f"# @accelerator(NPU) - fungsi {node.nama} pakai NPU")
            
            # Tanda tangan fungsi
            params = ", ".join([p.nilai for p in node.parameter])
            self.kode.append(self._tab() + f"def {node.nama}({params}):")
            self.indentasi += 1
            
            for stmt in node.tubuh:
                self.transpile(stmt)
            
            self.indentasi -= 1
            self.fungsi_aktif = None
            self.kode.append("")  # Baris kosong
        
        elif isinstance(node, PernyataanKembali):
            if node.nilai:
                self.kode.append(self._tab() + f"return {self.transpile(node.nilai)}")
            else:
                self.kode.append(self._tab() + "return None")
        
        elif isinstance(node, PernyataanCetak):
            self.kode.append(self._tab() + f"print({self.transpile(node.ekspresi)})")
        
        elif isinstance(node, PernyataanJika):
            self.kode.append(self._tab() + f"if {self.transpile(node.kondisi)}:")
            self.indentasi += 1
            for stmt in node.tubuh:
                self.transpile(stmt)
            self.indentasi -= 1
            
            if node.selain:
                if isinstance(node.selain, PernyataanJika):
                    self.kode.append(self._tab() + f"elif {self.transpile(node.selain.kondisi)}:")
                    self.indentasi += 1
                    for stmt in node.selain.tubuh:
                        self.transpile(stmt)
                    self.indentasi -= 1
                else:  # else biasa
                    self.kode.append(self._tab() + "else:")
                    self.indentasi += 1
                    for stmt in node.selain:
                        self.transpile(stmt)
                    self.indentasi -= 1
        
        elif isinstance(node, PernyataanUlangi):
            # Konversi ke while loop Python
            init = self.transpile(node.inisialisasi)
            self.kode.append(self._tab() + f"{init}")
            self.kode.append(self._tab() + f"while {self.transpile(node.kondisi)}:")
            self.indentasi += 1
            for stmt in node.tubuh:
                self.transpile(stmt)
            self.kode.append(self._tab() + f"    {self.transpile(node.iterasi)}")
            self.indentasi -= 1
        
        elif isinstance(node, PernyataanUntukSetiap):
            iterable = self.transpile(node.iterable)
            self.kode.append(self._tab() + f"for {node.variabel} in {iterable}:")
            self.indentasi += 1
            for stmt in node.tubuh:
                self.transpile(stmt)
            self.indentasi -= 1
        
        elif isinstance(node, PernyataanUlangiSelama):
            self.kode.append(self._tab() + f"while {self.transpile(node.kondisi)}:")
            self.indentasi += 1
            for stmt in node.tubuh:
                self.transpile(stmt)
            self.indentasi -= 1
        
        elif isinstance(node, PernyataanImport):
            self.kode.append(f"# import {node.modul}")
            self.kode.append(f"# (Implementasi import khusus Maden)")
        
        elif isinstance(node, EkspresiPenugasan):
            if node.anotasi:
                for anotasi in node.anotasi:
                    if anotasi.tipe == "INT8":
                        self.kode.append(self._tab() + f"# @int8 - variabel {node.nama} 8-bit")
                    elif anotasi.tipe == "INT128":
                        self.kode.append(self._tab() + f"# @int128 - variabel {node.nama} 128-bit")
            self.kode.append(self._tab() + f"{node.nama} = {self.transpile(node.nilai)}")
        
        elif isinstance(node, EkspresiVariabel):
            return node.nama
        
        elif isinstance(node, EkspresiAngka):
            return str(node.nilai)
        
        elif isinstance(node, EkspresiTeks):
            return f'"{node.nilai}"'
        
        elif isinstance(node, EkspresiBoolean):
            return str(node.nilai)
        
        elif isinstance(node, EkspresiBinOp):
            kiri = self.transpile(node.kiri)
            kanan = self.transpile(node.kanan)
            
            # Operator logika
            if node.operator == 'not':
                return f"not {kanan}"
            return f"({kiri} {node.operator} {kanan})"
        
        elif isinstance(node, EkspresiPanggilan):
            argumen = ", ".join([self.transpile(a) for a in node.argumen])
            return f"{node.nama}({argumen})"
        
        return str(node)
    
    def _tab(self) -> str:
        return "    " * self.indentasi
