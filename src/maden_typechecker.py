# maden_typechecker.py
from maden_parser_v2 import *
from maden_types import Tipe, TipeData

class TypeChecker:
    def __init__(self):
        self.errors = []
        self.fungsi_aktif = None
        self.fungsi_return_type = None
    
    def cek(self, node):
        if isinstance(node, Program):
            for stmt in node.pernyataan:
                self.cek(stmt)
        
        elif isinstance(node, PernyataanFungsi):
            self.fungsi_aktif = node.nama
            self.fungsi_return_type = node.tipe_kembali
            for stmt in node.tubuh:
                self.cek(stmt)
            self.fungsi_aktif = None
            self.fungsi_return_type = None
        
        elif isinstance(node, PernyataanKembali):
            if node.nilai is None:
                if self.fungsi_return_type.tipe != TipeData.KOSONG:
                    self.errors.append(f"Error: Fungsi '{self.fungsi_aktif}' harus mengembalikan {self.fungsi_return_type}, tapi tidak ada nilai")
                return
            tipe = self.cek(node.nilai)
            if self.fungsi_return_type and tipe != self.fungsi_return_type:
                self.errors.append(f"Error: Tipe return {tipe} tidak cocok dengan {self.fungsi_return_type} di fungsi '{self.fungsi_aktif}'")
        
        elif isinstance(node, PernyataanCetak):
            self.cek(node.ekspresi)
        
        elif isinstance(node, PernyataanJika):
            tipe_kondisi = self.cek(node.kondisi)
            if tipe_kondisi.tipe != TipeData.BOOL:
                self.errors.append(f"Error: Kondisi if harus bool, dapat {tipe_kondisi}")
            for stmt in node.tubuh:
                self.cek(stmt)
            if node.selain:
                if isinstance(node.selain, list):
                    for stmt in node.selain:
                        self.cek(stmt)
                else:
                    self.cek(node.selain)
        
        elif isinstance(node, PernyataanUlangi):
            self.cek(node.inisialisasi)
            tipe_kondisi = self.cek(node.kondisi)
            if tipe_kondisi.tipe != TipeData.BOOL:
                self.errors.append(f"Error: Kondisi loop harus bool, dapat {tipe_kondisi}")
            self.cek(node.iterasi)
            for stmt in node.tubuh:
                self.cek(stmt)
        
        elif isinstance(node, PernyataanUntukSetiap):
            # Cek iterable
            tipe_iterable = self.cek(node.iterable)
            if tipe_iterable.tipe != TipeData.ARRAY:
                self.errors.append(f"Error: 'untuk setiap' membutuhkan array, dapat {tipe_iterable}")
            for stmt in node.tubuh:
                self.cek(stmt)
        
        elif isinstance(node, PernyataanUlangiSelama):
            tipe_kondisi = self.cek(node.kondisi)
            if tipe_kondisi.tipe != TipeData.BOOL:
                self.errors.append(f"Error: Kondisi while harus bool, dapat {tipe_kondisi}")
            for stmt in node.tubuh:
                self.cek(stmt)
        
        elif isinstance(node, EkspresiPenugasan):
            tipe_nilai = self.cek(node.nilai)
            node.tipe = tipe_nilai
            # Cek apakah variabel ada (akan di cek di runtime)
        
        elif isinstance(node, EkspresiVariabel):
            # Simbol sudah di cek di parser
            return node.tipe if hasattr(node, 'tipe') else Tipe(TipeData.KOSONG)
        
        elif isinstance(node, EkspresiAngka):
            return node.tipe
        
        elif isinstance(node, EkspresiTeks):
            return node.tipe
        
        elif isinstance(node, EkspresiBoolean):
            return node.tipe
        
        elif isinstance(node, EkspresiArray):
            for el in node.elemen:
                self.cek(el)
            return node.tipe
        
        elif isinstance(node, EkspresiBinOp):
            tipe_kiri = self.cek(node.kiri)
            tipe_kanan = self.cek(node.kanan)
            
            # Operator perbandingan
            if node.operator in ['>', '<', '>=', '<=', '==', '!=']:
                if tipe_kiri != tipe_kanan:
                    self.errors.append(f"Error: Tipe tidak cocok untuk perbandingan: {tipe_kiri} vs {tipe_kanan}")
                node.tipe = Tipe(TipeData.BOOL)
                return node.tipe
            
            # Operator logika
            if node.operator in ['&&', '||']:
                if tipe_kiri.tipe != TipeData.BOOL or tipe_kanan.tipe != TipeData.BOOL:
                    self.errors.append(f"Error: Operator logika membutuhkan bool, dapat {tipe_kiri} dan {tipe_kanan}")
                node.tipe = Tipe(TipeData.BOOL)
                return node.tipe
            
            # Operator aritmatika
            if node.operator in ['+', '-', '*', '/', '%']:
                if tipe_kiri.tipe not in [TipeData.INT, TipeData.FLOAT] or tipe_kanan.tipe not in [TipeData.INT, TipeData.FLOAT]:
                    self.errors.append(f"Error: Operator aritmatika membutuhkan angka, dapat {tipe_kiri} dan {tipe_kanan}")
                # Tipe hasil = float jika salah satu float
                if tipe_kiri.tipe == TipeData.FLOAT or tipe_kanan.tipe == TipeData.FLOAT:
                    node.tipe = Tipe(TipeData.FLOAT)
                else:
                    node.tipe = Tipe(TipeData.INT)
                return node.tipe
            
            node.tipe = Tipe(TipeData.KOSONG)
            return node.tipe
        
        elif isinstance(node, EkspresiPanggilan):
            # Cek argumen (type checking akan dilakukan di runtime)
            for arg in node.argumen:
                self.cek(arg)
            node.tipe = Tipe(TipeData.KOSONG)
            return node.tipe
        
        return Tipe(TipeData.KOSONG)
    
    def cek_error(self):
        return self.errors