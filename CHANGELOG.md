# Changelog

## [1.0.0] - 2026-09-18

### Added

- Lexer JavaScript untuk sintaks Maden.
- Parser dan AST untuk fungsi, kondisi, loop, ekspresi, dan pemanggilan fungsi.
- Interpreter JavaScript tanpa `eval` atau `new Function`.
- Array dengan sintaks `[ ... ]`.
- Loop `untuk setiap ... dalam ...`.
- Runner browser melalui `maden.html`.
- Penyimpanan kode menggunakan `localStorage`.
- Tampilan token untuk membantu debugging.
- Smoke test Node.js untuk fitur inti dan array.
- Perintah `npm test` melalui `package.json`.

### Verification

```bash
npm test
```

Program contoh browser:

```maden
angka = [1, 2, 3]

untuk setiap nilai dalam angka {
    cetak(nilai)
}
```
