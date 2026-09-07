# maden_types.py
from enum import Enum
from typing import Any, Optional, List

class TipeData(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOL = "bool"
    ARRAY = "array"
    FUNGSI = "fungsi"
    KOSONG = "kosong"

class Tipe:
    def __init__(self, tipe: TipeData, elemen_tipe: Optional['Tipe'] = None):
        self.tipe = tipe
        self.elemen_tipe = elemen_tipe  # Untuk array
    
    def __repr__(self):
        if self.tipe == TipeData.ARRAY:
            return f"array<{self.elemen_tipe}>"
        return self.tipe.value
    
    def __eq__(self, other):
        if not isinstance(other, Tipe):
            return False
        if self.tipe != other.tipe:
            return False
        if self.tipe == TipeData.ARRAY:
            return self.elemen_tipe == other.elemen_tipe
        return True

class Simbol:
    def __init__(self, nama: str, tipe: Tipe, nilai: Any = None, anotasi: List[str] = None):
        self.nama = nama
        self.tipe = tipe
        self.nilai = nilai
        self.anotasi = anotasi or []

class TabelSimbol:
    def __init__(self):
        self.simbol = {}
        self.scope_stack = [{}]
    
    def masuk_scope(self):
        self.scope_stack.append({})
    
    def keluar_scope(self):
        self.scope_stack.pop()
    
    def tambah(self, nama: str, tipe: Tipe, nilai: Any = None, anotasi: List[str] = None):
        if nama in self.scope_stack[-1]:
            raise SyntaxError(f"Variabel '{nama}' sudah dideklarasikan di scope ini")
        self.scope_stack[-1][nama] = Simbol(nama, tipe, nilai, anotasi)
    
    def cari(self, nama: str) -> Optional[Simbol]:
        for scope in reversed(self.scope_stack):
            if nama in scope:
                return scope[nama]
        return None
    
    def update(self, nama: str, nilai: Any):
        for scope in reversed(self.scope_stack):
            if nama in scope:
                scope[nama].nilai = nilai
                return
        raise NameError(f"Variabel '{nama}' tidak ditemukan")

# Inferensi tipe
def infer_tipe(nilai) -> Tipe:
    if isinstance(nilai, int):
        return Tipe(TipeData.INT)
    elif isinstance(nilai, float):
        return Tipe(TipeData.FLOAT)
    elif isinstance(nilai, str):
        return Tipe(TipeData.STRING)
    elif isinstance(nilai, bool):
        return Tipe(TipeData.BOOL)
    elif isinstance(nilai, list):
        if nilai:
            elemen_tipe = infer_tipe(nilai[0])
            return Tipe(TipeData.ARRAY, elemen_tipe)
        return Tipe(TipeData.ARRAY, Tipe(TipeData.KOSONG))
    elif nilai is None:
        return Tipe(TipeData.KOSONG)
    return Tipe(TipeData.KOSONG)