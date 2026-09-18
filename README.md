# Maden 1.0

Maden adalah bahasa pemrograman berbahasa Indonesia yang berjalan langsung di browser tanpa Python.

## Menjalankan

Buka `maden.html` melalui browser atau Preview Acode. Pastikan folder `src-js` berada di samping file tersebut.

## Contoh

```maden
fungsi kuadrat(x) {
    kembali x * x
}

angka = [1, 2, 3]
untuk setiap nilai dalam angka {
    cetak(kuadrat(nilai))
}
```

Hasil:

```text
1
4
9
```

## Fitur versi 1.0

- angka, teks, boolean (`benar`, `salah`), dan `kosong`
- variabel dan assignment
- fungsi, parameter, dan `kembali`
- `cetak(...)`
- `jika` / `selain`
- `ulangi selama`
- array dengan `[ ... ]`
- `untuk setiap ... dalam ...`
- operator matematika, perbandingan, dan logika
- penyimpanan kode di `localStorage`
- pesan error dengan baris dan kolom dari lexer/parser

## Pengujian Node.js

Jalankan:

```bash
node tests-js/maden-smoke.test.js
```

Maden menggunakan JavaScript hanya sebagai host interpreter. Kode Maden tidak diubah menjadi JavaScript dan tidak dieksekusi dengan `eval` atau `new Function`.
